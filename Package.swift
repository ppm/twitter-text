// swift-tools-version:5.3
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
            url: "https://github.com/ppm/twitter-text/releases/download/v3.1.0-spm.2/TwitterText.xcframework.zip",
            checksum: "765cd9c52c019b4f41e20fc9e5449f40a3f6cb9b2393ee8c9eecf76ed13a87e9"
        )
    ]
)
