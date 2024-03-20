//
//  ContentView.swift
//  BTLE-Demo
//
//  Created by Chris Nurre on 1/4/21.
//

import SwiftUI

struct ContentView: View {
    @Bindable var btleObj = BTLEObject()

    var body: some View {
        VStack {
            Slider(value: $btleObj.number)
            Text("Number: \(btleObj.number)")
        }.padding()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
