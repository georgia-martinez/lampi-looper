//
//  ContentView.swift
//  Lampi-Looper
//
//  Created by Georgia Martinez on 4/18/24.
//

import SwiftUI

struct LampiView: View {
    @State private var loops = [
        Loop(name: "loop 1"),
        Loop(name: "loop 2"),
        Loop(name: "loop 3"),
    ]

    var body: some View {
        NavigationView {
            List {
                ForEach(loops) { loop in
                    LoopListView(loop: loop)
                }
                .onDelete { indexSet in
                    loops.remove(atOffsets: indexSet)
                }
            }
            .navigationTitle("My Loops")
            .navigationBarItems(trailing: EditButton())
        }
    }
}

struct LampiView_Previews: PreviewProvider {
    static var previews: some View {
        LampiView()
    }
}
