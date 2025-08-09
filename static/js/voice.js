// voice.js
// Handles Speech-to-Text (STT) and Text-to-Speech (TTS)

// ----- SPEECH TO TEXT -----
let recognition;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false; // Stop after user finishes speaking
    recognition.interimResults = false; // Only get final result
    recognition.lang = 'en-US';
} else {
    alert("Speech recognition is not supported in this browser. Please use Chrome.");
}

// Start listening for user speech
function startListening() {
    if (!recognition) return;
    recognition.start();

    recognition.onstart = function () {
        console.log("Voice recognition started. Speak now...");
        document.getElementById("status").innerText = "Listening...";
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        console.log("User said:", transcript);
        document.getElementById("answer").value = transcript; // Put it in input box
        document.getElementById("status").innerText = "Captured voice input.";
    };

    recognition.onerror = function (event) {
        console.error("Speech recognition error:", event.error);
        document.getElementById("status").innerText = "Error capturing voice.";
    };

    recognition.onend = function () {
        console.log("Voice recognition ended.");
        document.getElementById("status").innerText = "Stopped listening.";
    };
}

// ----- TEXT TO SPEECH -----
function speak(text) {
    if (!'speechSynthesis' in window) {
        alert("Text-to-Speech not supported in this browser.");
        return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1; // Speed
    utterance.pitch = 1; // Tone
    speechSynthesis.speak(utterance);
}

// Example usage:
// speak("Hello, welcome to the AI interview bot!");
// startListening();
