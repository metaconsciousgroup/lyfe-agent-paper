# lyfe-python-env
Lightweight package to connect the Lyfe Game to python

# For developers
## Environment Setup
- Install Anaconda: https://docs.anaconda.com/free/anaconda/install/
- Open terminal, go to the project directory
- Create a virtual environment `conda create --name unity python=3.9`
- Activate the environment `conda activate unity`
- Now install this package with `pip install -e .` in command line (remember to include the `.` at the end, `-e` means you can keep editing the package)

## Run the game
- first run `conda activate unity` in command line **every time** you want to run the python script.
- In some systems, you may need `activate unity` instead to activate the virtual environment.
- run `python main.py` to use the Unity binary build
- run `python main.py --editor` to use the Unity Editor version
    - NOTE that Python script needs to start *before* clicking start on Unity editor.

## Note
- To run python script, please make sure you are in the correct environment
- Build the game first and save it into the `./Builds/macOS` or `./Builds/Windows` or `./Builds/Linux` folder, depending on the type of the game build
- Name the build file as `genagentminimal`

