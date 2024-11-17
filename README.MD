# Website Design Generator

Welcome to the Website Design Generator project! This tool helps you create stunning website designs effortlessly.

## Features

- **Easy to Use**: User-friendly interface for quick design generation.
- **Customizable Templates**: Choose from a variety of templates and customize them to fit your needs.
- **Export Options**: Export your designs in HTML, CSS, and JavaScript.

## Installation

To get started, follow these steps:

1. **Clone the repository**:

   Open your terminal and run the following command to clone the repository:

   ```bash
   git clone https://github.com/devanmolsharma/WebsiteBuilder.git
   ```

2. **Navigate to the project directory**:

   Change your current directory to the project directory:

   ```bash
   cd WebsiteBuilder
   ```

## Usage

1. **Install the required dependencies**:

   Make sure you have `pip` and `npm` installed on your system. Then, run the following command to install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Next, install the Node.js dependencies:

   ```bash
   npm install
   ```

2. **Run the development server**:

   Start the Django development server by running:

   ```bash
   python manage.py runserver
   ```

3. **Handle all CSS files**:

   In a new terminal window, navigate to the project directory and run the following command to watch and compile CSS files:

   ```bash
   npm run watch
   ```

4. **Open your browser**:

   Open your web browser and navigate to `http://localhost:8000` to access the application.

5. **Start designing your website**:

   Use the interface to start creating and customizing your website designs.

6. **Add your Stable Diffusion key**:

   Open the `config.py` file located at `homepage/utils/generateImage/` and add your Stable Diffusion key.

   If you don't have a Stable Diffusion key, you can obtain one by signing up on [DreamStudio](https://dreamstudio.ai/). Follow these steps:

   1. **Sign Up**: Go to the DreamStudio website and create an account.
   2. **Generate API Key**: Once logged in, navigate to the API section and generate a new API key.
   3. **Copy the Key**: Copy the generated API key and paste it into the `config.py` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please contact us at [keepupsharma@gmail.com](mailto:keepupsharma@gmail.com).

Happy designing!
