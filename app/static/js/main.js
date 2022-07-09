let mic;
let fft;

function getFreqSpectrum() {
    let frequencies = fft.analyze();
    console.log(frequencies);
}

function setup() {
    // mic = new p5.AudioIn();
    // mic.start();
    // fft = new p5.FFT();
    // fft.setInput(mic);
    // setTimeout(getFreqSpectrum, 10000); // do this in 10 seconds
}