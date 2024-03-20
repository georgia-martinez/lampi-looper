//
//  Lampi.swift
//  Lampi
//

import Foundation
import SwiftUI

@Observable class Lampi {
    var hue: Double = 1.0
    var saturation: Double = 1.0
    var brightness: Double = 1.0

    var isOn = false

    var color: Color {
        Color(hue: hue, saturation: saturation, brightness: brightness)
    }

    var baseHueColor: Color {
        Color(hue: hue, saturation: 1.0, brightness: 1.0)
    }
}
