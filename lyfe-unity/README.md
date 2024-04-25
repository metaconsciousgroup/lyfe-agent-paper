# Mock Lyfe Game
## Environment Setup
- Install Anaconda: https://docs.anaconda.com/free/anaconda/install/
- Open terminal, go to the project directory
- run `conda env create -f environment.yaml` in command line

## Run the game
- first run `conda activate unity` in command line **every time** you want to run the python script.
- In some systems, you may need `activate unity` instead to activate the virtual environment.
- run `python main.py` to use the Unity binary build
- run `python main.py --editor` to use the Unity Editor version
    - NOTE that Python script needs to start *before* clicking start on Unity editor.

## Note
- To run python script, please make sure you are in the correct environment
- Build the game first and save it into the `./Builds` folder, depending on the type of the game build
- Name the build file as `genagentminimal`


## Run web client locally

Build a WebGL version with Brotli compression (default option) at `Builds/WebGL/LyfeGameClient`. You can also use the build it through the Unity editor using `Build -> Build WebGL Client`.

The folder structure should looks something similar to 
```
Builds
  - WebGL
    - LyfeGameClient
      - Build
        - LyfeGameClient.data.br
        - LyfeGameClient.framework.js.br
        - LyfegameClient.loader.js
        - LyfeGameClient.wasm.br
      - StreamingAssets
      - TemplateData
      - index.html
    - server.js (This is included as a Node.js server, not built by Unity)
```

Run the WebGL build locally with `npm start`. Open a browser and direct to `http://localhost:8001`. If you don't have Node.js, use the following commands to set it up.

### Setup Node.js (one-time)

- Install Node.js through the official website, https://nodejs.org/en

- Run the following command to setup the server. This will create a `node_modules` folder, a `package-lock.json` and `package.json` file. As long as these files are still there, there is no need to rerun the following commands.

```
cd Builds/WebGL
npm init -y
npm install express
npm install cors
```
