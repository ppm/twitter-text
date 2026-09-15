#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess


def run(*args):
    try:
        return subprocess.check_output(args, text=True).strip()
    except subprocess.CalledProcessError as error:
        if error.output:
            print(error.output)
        raise


def manifest(repository, version, checksum):
    return f'''// swift-tools-version:5.3
//
//  Package.swift
//  TwitterTextBinary
//
//  Created by ppm on 2026/09/14.
//

import PackageDescription

let package = Package(
    name: "TwitterTextBinary",
    platforms: [.iOS(.v9), .macOS(.v10_12)],
    products: [.library(name: "TwitterText", targets: ["TwitterText"])],
    targets: [
        .binaryTarget(
            name: "TwitterText",
            url: "https://github.com/{repository}/releases/download/{version}/TwitterText.xcframework.zip",
            checksum: "{checksum}"
        )
    ]
)
'''


def package(products):
    destination = Path('build/release').resolve()
    destination.mkdir(parents=True, exist_ok=False)
    framework = destination / 'TwitterText.xcframework'
    args = ['xcodebuild', '-create-xcframework']
    for configuration in ['Release-iphoneos', 'Release-iphonesimulator', 'Release']:
        args += ['-framework', str(products.resolve() / configuration / 'TwitterText.framework')]
    run(*args, '-output', str(framework))
    shutil.copy('objc/LICENSE', framework / 'LICENSE')
    shutil.copy('objc/ThirdParty/IFUnicodeURL/IFUnicodeURL-LICENSE.txt', framework)
    shutil.copy('scripts/licenses/IDNSDK-LICENSE.txt', framework)
    archive = destination / 'TwitterText.xcframework.zip'
    run('ditto', '-c', '-k', '--keepParent', str(framework), str(archive))
    return archive


def prepare(repository, version):
    archive = Path('build/release/TwitterText.xcframework.zip')
    checksum = run('swift', 'package', 'compute-checksum', str(archive))
    package_file = Path('build/release/Package.swift')
    package_file.write_text(manifest(repository, version, checksum))
    source = run('git', 'rev-parse', 'HEAD')
    notes = Path('build/release/notes.md')
    notes.write_text(f'XCFramework built from {source}.\n\nSHA-256: `{checksum}`\n')
    run('gh', 'release', 'create', version, str(archive), str(package_file),
        '--repo', repository, '--draft', '--target', source,
        '--title', version, '--notes-file', str(notes),
        '--prerelease=' + str('-' in version).lower())
    branch = f'release/{version}'
    run('git', 'switch', '-c', branch)
    shutil.copy(package_file, 'Package.swift')
    run('git', 'add', 'Package.swift')
    run('git', 'commit', '-m', f'Publish TwitterText binary package {version}')
    run('git', 'push', '-u', 'origin', 'HEAD')
    base = run('gh', 'repo', 'view', repository, '--json', 'defaultBranchRef', '--jq', '.defaultBranchRef.name')
    print(run('gh', 'pr', 'create', '--repo', repository, '--base', base, '--head', branch,
              '--title', f'Publish TwitterText binary package {version}', '--body-file', str(notes)))


def resume(repository, version):
    release = json.loads(run('gh', 'release', 'view', version, '--repo', repository,
                             '--json', 'isDraft,targetCommitish,body'))
    if not release['isDraft']:
        raise SystemExit('Release is already published.')
    branch = f'release/{version}'
    run('git', 'fetch', 'origin', f'refs/heads/{branch}')
    source = release['targetCommitish']
    run('git', 'merge-base', '--is-ancestor', source, 'FETCH_HEAD')
    run('git', 'diff', '--exit-code', source, 'FETCH_HEAD', '--', '.', ':(exclude)Package.swift')
    destination = Path('build/resume')
    destination.mkdir(parents=True, exist_ok=False)
    run('gh', 'release', 'download', version, '--repo', repository, '--dir', str(destination))
    checksum = run('swift', 'package', 'compute-checksum', str(destination / 'TwitterText.xcframework.zip'))
    expected = manifest(repository, version, checksum)
    if run('git', 'show', 'FETCH_HEAD:Package.swift') != expected.strip() or (destination / 'Package.swift').read_text() != expected:
        raise SystemExit('Release branch does not match the draft assets.')
    existing = json.loads(run('gh', 'pr', 'list', '--repo', repository, '--head', branch,
                              '--state', 'all', '--json', 'url'))
    if existing:
        print(existing[0]['url'])
        return
    notes = destination / 'notes.md'
    notes.write_text(release['body'])
    base = run('gh', 'repo', 'view', repository, '--json', 'defaultBranchRef', '--jq', '.defaultBranchRef.name')
    print(run('gh', 'pr', 'create', '--repo', repository, '--base', base, '--head', branch,
              '--title', f'Publish TwitterText binary package {version}', '--body-file', str(notes)))


def publish(repository, version):
    release = json.loads(run('gh', 'release', 'view', version, '--repo', repository,
                             '--json', 'isDraft,targetCommitish'))
    if not release['isDraft']:
        raise SystemExit('Release is already published.')
    source = release['targetCommitish']
    run('git', 'merge-base', '--is-ancestor', source, 'HEAD')
    run('git', 'diff', '--exit-code', source, 'HEAD', '--', '.', ':(exclude)Package.swift',
        ':(exclude)scripts/release.py', ':(exclude).github/workflows/release.yml',
        ':(exclude).github/RELEASING.md')
    destination = Path('build/publish')
    destination.mkdir(parents=True, exist_ok=False)
    run('gh', 'release', 'download', version, '--repo', repository, '--dir', str(destination))
    checksum = run('swift', 'package', 'compute-checksum', str(destination / 'TwitterText.xcframework.zip'))
    expected = manifest(repository, version, checksum)
    if Path('Package.swift').read_text() != expected or (destination / 'Package.swift').read_text() != expected:
        raise SystemExit('Merge the matching Package.swift PR before publishing.')
    if run('git', 'ls-remote', '--tags', 'origin', f'refs/tags/{version}'):
        raise SystemExit('Tag already exists; choose a new version.')
    run('gh', 'release', 'edit', version, '--repo', repository,
        '--target', run('git', 'rev-parse', 'HEAD'), '--draft=false')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['package', 'prepare', 'resume', 'publish'])
    parser.add_argument('--products', type=Path)
    parser.add_argument('--repository')
    parser.add_argument('--version')
    args = parser.parse_args()
    if args.operation == 'package':
        if args.products is None:
            parser.error('--products is required')
        print(package(args.products))
    else:
        if not args.repository or not args.version or not re.fullmatch(r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?', args.version):
            parser.error('--repository and a semantic --version are required')
        {'prepare': prepare, 'resume': resume, 'publish': publish}[args.operation](args.repository, args.version)
