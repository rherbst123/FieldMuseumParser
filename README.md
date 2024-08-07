
# Herbarium Specimen Image Processor
## Version 1.0

This project provides a graphical user interface (GUI) application for processing and viewing images of herbarium specimens. The application allows users to easily load, view, and manipulate images, making it an essential tool for botanists and researchers working with herbarium collections.

## Requirements

To run this project, you'll need to have the following packages installed:

- anthropic
- numpy
- pandas
- requests
- pillow
- openai
- tkinter
- ttkbootstrap

## Future Updates

- [ ] Window for .CSV editing.
- [ ] Support for Open AI and Local LLM's 
- [ ] Containerize and have executable 


You can install these dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Usage

1. Clone the repository:

```bash
git clone https://github.com/yourusername/herbarium-image-processor.git
cd herbarium-image-processor
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Setting Up a Python Virtual Environment (venv) (Optional)

It's recommended to use a virtual environment to manage your project dependencies. Follow these steps to set up a virtual environment:

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS and Linux:

```bash
source venv/bin/activate
```

3. Install the required dependencies within the virtual environment:

```bash
pip install -r requirements.txt
```

## In GUI

1. For URL's of images: URL's must lead to full size image directly. (Find example in inputs/image URL test.txt)

2. API key File: As of version 1.0 Only Anthropics Claude is usable. (Must be in .txt file)

3. Prompts in Inputs/Prompts.
Dropdown will refresh after choosing folder.

4. Output File must be .txt 

## Acknowledgements

Special thanks to Matt Von Konrat, Jeff Gwillam, Dan Stille, Rick Ree and the Field Museum.
