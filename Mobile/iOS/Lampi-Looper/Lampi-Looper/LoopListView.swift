//
//  LoopView.swift
//  Lampi-Looper
//
//  Created by Georgia Martinez on 4/18/24.
//

import SwiftUI

struct LoopListView: View {
    let loop: Loop
    @State private var isPlaying = false // State variable to track play/pause state
    
    var body: some View {
        HStack {
            Text(loop.name)
            Spacer()
            
            Button(action: {
                // Toggle play/pause state
                isPlaying.toggle()
            }) {
                // Use conditional rendering for the button icon
                Image(systemName: isPlaying ? "pause.fill" : "play.fill")
            }
            .padding(.trailing) // Add some padding to the button
        }
        .padding(.vertical, 8)
    }
}
