# goco-scraping

This is a guide for setting up the Go Columbia Lions scraper.
## Setup

1. Clone the repository and move into it:

```
$ git clone git@github.com:NewsroomDevelopment/goco-scraping.git
$ cd goco-scraping
```

3. If you're using Python: Run `pipenv install` to install the necessary packages. Run `pipenv shell` to launch the virtual environment and get access to those packages. If you do not have `pipenv` do `pip install pipenv`. If you do not have `pip` look it up.

4. In the shell, run do `python -m ipykernel install --user --name=goco`

5. Open up jupyter notebook and change the kernel by going to kernel -> change kernel -> goco.

6. To add dependencies, you can do pipenv install <package-name>. Then, restart the jupyter notebook and do step 4 again. This will make sure the jupyter notebook environment is up to date.

## Usage

Open up jupyter notebook and start coding!
