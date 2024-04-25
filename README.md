# Gen-Agents
🤖 Generative Agents in 3D Unity Environment

Project design doc [here](https://docs.google.com/document/d/1OgDKIHRjxaBe7FOwu-vo0Zq8bKGyRIJAT_YyJnZDLt8/edit?usp=sharing)

- For users

  Thank you for your interest in generative agents. Please use `git clone` to get codes in `dev` branch.

- For developers

  Please start by creating a new branch and push your local changes to this new branch, before merging to `dev`. **Let us try to keep `dev` branch working correctly. Thank you!**

## ⏬ Installation

Ensure SSH keys are set up for public and private access. Follow these steps:
1. [Generate a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key).
2. [Add the SSH key to your agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#adding-your-ssh-key-to-the-ssh-agent).
3. [Associate the SSH key with your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account).

After preparations, follow these steps:

1. Navigate to the `gen-agent` directory: `cd gen-agent`.
2. Ensure Python 3.9 is installed.
3. Create the Conda environment: `conda env create -f environment.yaml python=3.9`.
   - The `environment.yaml` specifies the environment name.
   - Activate the environment with `conda activate gen`.
   - For reinstallation, use `conda env remove --name gen` or install packages manually.
4. Confirm installation: `conda env list` or `conda info --envs`.
5. Set the default path: `conda develop .`.
6. Always activate the environment before working: `conda activate gen`.

## 🌟 Quick Start of Your Journey

### 1. Setup API Keys

- "Secrets" such as API keys should be stored locally in a file that is not version controlled.
- We store it in a `.env` file in the root folder `gen-agent/.env`.

#### OpenAI API Setup
- Use API keys from Google Drive: [OpenAI API Key](https://docs.google.com/document/d/1667orJl8R1t7O7OMi91lyfRc4KoJhYKunVeLHD-YOwc/edit?usp=sharing)
  - There might be errors connecting to the OpenAI Server, please retry if this happens.
- **API Keys Setup**:
  - **For User**: Store at least one API key to your local repo by adding `OPENAI_APIKEY=abcd123` (no extra space).
  - **For Developer**: You can add other API keys similarly. The API keys will be loaded at runtime by `settings.py`.

#### Pinecone Setup (Optional: For non-local memory architecture)
- If you wish to use a non-local memory architecture, Pinecone can be set up. Note: It will take longer to load the games (~2 min).
- Steps to set up Pinecone:
  1. Create an account on Pinecone.
  2. Create a Project and select as environment `us-west4-gcp-free` (this will be the variable `PINECONE_ENVIRONMENT`).
  3. Enter the project and create a Pinecone index: give it an index name (this will be the variable `PINECONE_INDEX`) and fill in dimension as `1536`.
  4. Once the index is successfully created, click on "API Keys" on the left side nav and create an API key (`PINECONE_APIKEY`).

- In the `.env` file, add the following details from Pinecone:

```
PINECONE_APIKEY=<Your-API-Key>
PINECONE_ENVIRONMENT=<Your-Environment-Value>
PINECONE_INDEX=<Your-Index-Name>
```

Ensure to replace `<Your-API-Key>`, `<Your-Environment-Value>`, and `<Your-Index-Name>` with the appropriate values from the Pinecone website (no extra space).

### 2. Running a text-only demo
Run Python file `python main.py --config-name demo_conv` for interactions between a group of language-model-powered agents.

### 3. Running a Unity demo

Run Python file `python main.py --config-name demo_unity` for Unity environment demo (the latest working demo may change). 
This requires the proper Unity environment binary **(see <u>Want to play with Unity?</u> part below)**.

### 4. Analyzing Run Outcomes

Experiment outcomes are stored in the `outputs` or `multirun` folders. Navigate to your experiment's folder to find a `.log` file containing all conversation logs.

- Analysis code is located in the `analysis` folder, where you can use pre-built functions for quantitative analysis. You can also create custom functions in `/analysis/analysis_utils.py` and `/analysis/plot_utils.py`.

### 5. Contributing a New Scenario

To contribute a new scenario, add a new config file to the `configs` folder.

- Config `.yaml` file structure (Basic settings)
  - `configs/agents` folder: Contains agent background information (e.g., name, personality, city, memories). You are supposed to write background story yourself if you create a `yaml` file here, otherwise, go to see `configs/generative`
  - `configs/brain` folder: Contains high-level brain structures (e.g., brain functions like plan, talk, move, and memory size restrictions).
  - `configs/general` folder: Contains scenario-specific settings (e.g., iterations and random seed).
  - `configs/generative` folder: Set up basic keywords for agents, and let GPT generate whole backgrounds.
- Text-only demo:
  - Create a `.yaml` file following the pattern in `configs/demo_conv.yaml`.
- Unity-interaction demo:
  - Create a `.yaml` file following the pattern in `configs/demo_unity.yaml`.

## ⚙️ Want to play with Unity?

Download the latest build using the platform website. If it's not working, ask Shuying to send it to you.

For Mac users, put the executable file under Builds/macOS/LyfeGame
For Windows users, put the executable file under Builds/Windows/LyfeGame.exe

## 📚 Useful Resources
- AutoGPT
  - Automatically breaks down goals in natural language into sub-tasks and leverages the internet and other tools in a loop.
  - [GitHub Repository](https://github.com/Significant-Gravitas/Auto-GPT)
  - [Documentation](https://significant-gravitas.github.io/Auto-GPT/configuration/search/)
- [OpenAI Prompt Design](https://platform.openai.com/docs/guides/completion/prompt-design): Tips on writing effective prompts for GPT.
- Generative Agents: Interactive Simulacra of Human Behaviors - [Research Paper](https://arxiv.org/abs/2304.03442)
- Unity Toolkits
  - Avatar Creation: [Ready Player Me](https://docs.readyplayer.me/ready-player-me/integration-guides/unity)
  - Animation: [Mixamo](https://www.mixamo.com/#/)
  - Create animated avatars with Ready Player Me and Mixamo
    - [YouTube Tutorial](https://www.youtube.com/watch?v=Cg4k-XPBC2Q&t=7s)
    - [Related GitHub Repository](https://github.com/srcnalt/RPM-Smart-NPC)

## 📝 Formatting

- For Pycharm users, you can simply use shortcut `Option + Command + L` to format the code.
- For VSCode users, you can install the `Python` extension and set `"editor.formatOnSave": true` in your `settings.json` file.
- (TODO) Set up and use the `black` formatter.
