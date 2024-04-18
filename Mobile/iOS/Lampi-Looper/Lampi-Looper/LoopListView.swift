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
            // Upload button
            Image(systemName: "square.and.arrow.up")
                .padding()
                .onTapGesture {
                    
                }
            
            // Loop name
            Text(loop.name)
                .padding()
            
            Spacer()
            
            // Play button
            Image(systemName: isPlaying ? "pause.fill" : "play.fill")
                .padding()
                .onTapGesture {
                    isPlaying.toggle()
                }
        }
        .padding(.vertical, 8)
    }
}


