# OmniParserBLECC

A web-based UI for creating and executing automation scripts that interact with the UI of other applications.

## Project Structure

The project is organized as follows:

```
OmniParserBLECC/
├── scripts/                   # Python scripts created by the user
├── uipath_interface/          # Main Flask application
│   ├── app.py                 # Flask server
│   ├── static/                # Static assets
│   │   ├── css/               # Stylesheets
│   │   ├── js/                # JavaScript files
│   │   │   ├── main.js        # Main JavaScript entry point
│   │   │   ├── dragAndDrop.js # Drag and drop functionality
│   │   │   ├── nodeManager.js # Node creation and management
│   │   │   ├── scriptExecution.js # Script execution handling
│   │   │   ├── propertyPanel.js # Properties panel functionality
│   │   │   ├── csvUtils.js    # CSV-related functionality
│   │   │   └── uiUtils.js     # UI utility functions
│   │   └── img/               # Images
│   └── templates/             # HTML templates
│       └── index.html         # Main application page
└── README.md                  # This file
```

## Running the Application

To run the application:

1. Ensure Python 3.7+ is installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the Flask server:
   ```
   cd uipath_interface
   python app.py
   ```
4. Navigate to `http://localhost:5000` in your web browser

## Features

- Drag-and-drop interface for creating automation scripts
- Support for screen scopes to organize actions by UI context
- CSV loop functionality for data-driven automation
- Real-time script execution and feedback
- Properties panel for configuring actions and scopes
- Ability to save and load scripts

## API Endpoints

The application provides the following API endpoints:

- `/api/scripts` - Get a list of available scripts
- `/api/actions` - Get a list of available actions
- `/api/save_script` - Save a script
- `/api/run_script` - Run a script (SSE endpoint)
- `/api/stop_script` - Stop a running script
- `/api/get_csv_columns` - Get columns from a CSV file
- `/api/output/` - Access to output files (screenshots, etc.)

## Modularization

The JavaScript code has been modularized to improve maintainability and organization:

- `main.js`: Entry point, initializes the application
- `dragAndDrop.js`: Handles drag and drop functionality
- `nodeManager.js`: Manages the creation and updating of nodes
- `scriptExecution.js`: Handles script execution and interaction with the API
- `propertyPanel.js`: Manages the properties panel UI and form handling
- `csvUtils.js`: Handles CSV-related functionality
- `uiUtils.js`: Provides utility functions for UI elements

# OmniParser: Screen Parsing tool for Pure Vision Based GUI Agent

<p align="center">
  <img src="imgs/logo.png" alt="Logo">
</p>

[![arXiv](https://img.shields.io/badge/Paper-green)](https://arxiv.org/abs/2408.00203)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

📢 [[Project Page](https://microsoft.github.io/OmniParser/)] [[V2 Blog Post](https://www.microsoft.com/en-us/research/articles/omniparser-v2-turning-any-llm-into-a-computer-use-agent/)] [[Models V2](https://huggingface.co/microsoft/OmniParser-v2.0)] [[Models V1.5](https://huggingface.co/microsoft/OmniParser)] [[HuggingFace Space Demo](https://huggingface.co/spaces/microsoft/OmniParser-v2)]

**OmniParser** is a comprehensive method for parsing user interface screenshots into structured and easy-to-understand elements, which significantly enhances the ability of GPT-4V to generate actions that can be accurately grounded in the corresponding regions of the interface. 

## News
- [2025/3] We are gradually adding multi agents orchstration and improving user interface in OmniTool for better experience.
- [2025/2] We release OmniParser V2 [checkpoints](https://huggingface.co/microsoft/OmniParser-v2.0). [Watch Video](https://1drv.ms/v/c/650b027c18d5a573/EWXbVESKWo9Buu6OYCwg06wBeoM97C6EOTG6RjvWLEN1Qg?e=alnHGC)
- [2025/2] We introduce OmniTool: Control a Windows 11 VM with OmniParser + your vision model of choice. OmniTool supports out of the box the following large language models - OpenAI (4o/o1/o3-mini), DeepSeek (R1), Qwen (2.5VL) or Anthropic Computer Use. [Watch Video](https://1drv.ms/v/c/650b027c18d5a573/EehZ7RzY69ZHn-MeQHrnnR4BCj3by-cLLpUVlxMjF4O65Q?e=8LxMgX)
- [2025/1] V2 is coming. We achieve new state of the art results 39.5% on the new grounding benchmark [Screen Spot Pro](https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding/tree/main) with OmniParser v2 (will be released soon)! Read more details [here](https://github.com/microsoft/OmniParser/tree/master/docs/Evaluation.md).
- [2024/11] We release an updated version, OmniParser V1.5 which features 1) more fine grained/small icon detection, 2) prediction of whether each screen element is interactable or not. Examples in the demo.ipynb. 
- [2024/10] OmniParser was the #1 trending model on huggingface model hub (starting 10/29/2024). 
- [2024/10] Feel free to checkout our demo on [huggingface space](https://huggingface.co/spaces/microsoft/OmniParser)! (stay tuned for OmniParser + Claude Computer Use)
- [2024/10] Both Interactive Region Detection Model and Icon functional description model are released! [Hugginface models](https://huggingface.co/microsoft/OmniParser)
- [2024/09] OmniParser achieves the best performance on [Windows Agent Arena](https://microsoft.github.io/WindowsAgentArena/)! 

## Install 
First clone the repo, and then install environment:
```python
cd OmniParser
conda create -n "omni" python==3.12
conda activate omni
pip install -r requirements.txt
```

Ensure you have the V2 weights downloaded in weights folder (ensure caption weights folder is called icon_caption_florence). If not download them with:
```
   # download the model checkpoints to local directory OmniParser/weights/
   for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights; done
   mv weights/icon_caption weights/icon_caption_florence
```

<!-- ## [deprecated]
Then download the model ckpts files in: https://huggingface.co/microsoft/OmniParser, and put them under weights/, default folder structure is: weights/icon_detect, weights/icon_caption_florence, weights/icon_caption_blip2. 

For v1: 
convert the safetensor to .pt file. 
```python
python weights/convert_safetensor_to_pt.py

For v1.5: 
download 'model_v1_5.pt' from https://huggingface.co/microsoft/OmniParser/tree/main/icon_detect_v1_5, make a new dir: weights/icon_detect_v1_5, and put it inside the folder. No weight conversion is needed. 
``` -->

## Examples:
We put together a few simple examples in the demo.ipynb. 

## Gradio Demo
To run gradio demo, simply run:
```python
python gradio_demo.py
```

## Model Weights License
For the model checkpoints on huggingface model hub, please note that icon_detect model is under AGPL license since it is a license inherited from the original yolo model. And icon_caption_blip2 & icon_caption_florence is under MIT license. Please refer to the LICENSE file in the folder of each model: https://huggingface.co/microsoft/OmniParser.
 Prerequisites
## Required Software
- Python 3.8 or higher
- ffmpeg (required for video processing)

### Installing ffmpeg
#### macOS
Using Homebrew:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg
brew install ffmpeg

# Verify installation
ffmpeg -version
```

#### Windows
Using Chocolatey:
```bash
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install ffmpeg
choco install ffmpeg

# Verify installation
ffmpeg -version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install ffmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

#### Linux (Fedora)
```bash
# Install ffmpeg
sudo dnf install ffmpeg

# Verify installation
ffmpeg -version
```

### Troubleshooting ffmpeg Installation
If you encounter "command not found" errors after installation:
1. Make sure to restart your terminal/command prompt
2. Verify ffmpeg is in your system PATH:
   - Windows: Check if `C:\ProgramData\chocolatey\bin` is in your PATH
   - macOS/Linux: Run `which ffmpeg` to verify the installation path
3. If still not working, try:
   - Windows: Run `refreshenv` in a new terminal
   - macOS: Run `brew link ffmpeg`
   - Linux: Run `hash -r`

### Python Dependencies

## 📚 Citation
Our technical report can be found [here](https://arxiv.org/abs/2408.00203).
If you find our work useful, please consider citing our work:
```
@misc{lu2024omniparserpurevisionbased,
      title={OmniParser for Pure Vision Based GUI Agent}, 
      author={Yadong Lu and Jianwei Yang and Yelong Shen and Ahmed Awadallah},
      year={2024},
      eprint={2408.00203},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2408.00203}, 
}
```