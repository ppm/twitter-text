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
            url: "https://github.com/ppm/twitter-text/releases/download/v3.1.0-spm.1/TwitterText.xcframework.zip",
            checksum: "bd40b520ef36f56a7bf7e2e814d5289acb58b009bfb3332abc152bf2dd318949"
        )
    ]
)
