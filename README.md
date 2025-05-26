## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Third-Party Licenses

This project uses the following third-party libraries, each with their own license:

- pynput (LGPLv3)  
- Vosk (Apache 2.0)  
- PyAudio (MIT)  
- python-dotenv (BSD 3-Clause)

See [THIRD-PARTY-LICENSES.md](./THIRD-PARTY-LICENSES.md) for details.

## Disclaimer and Limitation of Liability

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

By using this software, you agree to use it at your own risk.


# 🎙️ Speech Monitor - Voice-Controlled Keyboard Automation

This Python tool uses the Vosk speech recognition engine to monitor microphone input and execute pre-configured keyboard actions when specific **command** words are spoken. Ideal for accessibility tools, voice-controlled games, or voice-command automation.

This is a modified Speech Monitor Voice-Controlled Keyboard Automation meant for dark soul 3, the full code will be relase at a later date

Mod showcase : (video will be relase at a later date)

---

## 🔧 Features

- Real-time speech recognition using [Vosk](https://alphacephei.com/vosk/)
- Detects **command** keywords in two modes: `full` (exact word match) and `partial` (sub-string match)
- Maps spoken words to custom keyboard actions
- Visual feedback with color highlighting in the terminal
- Easily extensible with custom callbacks

---

## 🧰 Requirements

- Python 3.7+
- `vosk`, `pyaudio`, `pynput`, `python-dotenv`

1. Install the Python dependencies (pip install -r requirements.txt).
2. Download a Vosk model separately.
3. Unzip the model.
4. Configure the VOSK_MODEL_PATH in their .env file to point to the downloaded and unzipped model.

Install dependencies:

```bash
pip install -r requirements.txt