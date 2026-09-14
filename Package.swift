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
        .binaryTarget(name: "TwitterText", path: "build/TwitterText.xcframework")
    ]
)
