import streamlit as st
from dotenv import find_dotenv, load_dotenv
from enum import Enum
from yt_dlp import YoutubeDL
from pydantic import BaseModel, HttpUrl, ValidationError
from loguru import logger
import urllib.request
import os

class MyUrl(BaseModel):
    url: HttpUrl


def url_isalive(url):
    code = urllib.request.urlopen(url).getcode()
    if code == 200:
        logger.info(f"Site {url} is Alive.")
        return True
    else:
        logger.error(f"Site {url} is Dead.")
        return False


def validate_url(url):
    try:
        MyUrl(url=url)
    except ValidationError as e:
        return False
    else:
        if url_isalive(url=url):
            return True
        else:
            st.error(f"{url} is not Alive.")
            return False


class Mytube(Enum):
    HOME_DIR = os.getenv("HOME")
    TARGET_DIR = os.getenv("TARGET_DIR")
    LAYOUT = "centered"
    TITLE = "MyTube :sunglasses:"
    LABEL = "Paste Youtube URL in this"
    FORMAT = "mp4"
    OUTTMPL = "%(artist)s-%(title)s.%(ext)s"
    LOGFILE = "mytube.log"


def download_yt(url):
    if not validate_url(url=url):
        logger.warning(f"Wrong url: {url}")
        st.warning("Your URL is wrong, check it out again.")

        return False
    else:
        logger.info(f"Start downloading from {url}")
        st.write(f"Start downloading from {url}")
        ydl_opts = {
            "outtmpl": Mytube.OUTTMPL.value,
        }
        with YoutubeDL(ydl_opts) as ydl:
            with st.spinner("Downloading..."):
                info_dict = ydl.extract_info(url, download=True)
                output_filename = ydl.prepare_filename(info_dict)
            st.success(f"Downloaded {output_filename}")
            logger.info(f"Successfully Download file {output_filename}")

    return output_filename


def delete_downloaded_file(filename):
    logger.info(f"User tries to download {filename} into its machine...")
    if os.path.exists(filename):
        os.remove(filename)


if __name__ == "__main__":
    # Set pages
    load_dotenv(find_dotenv(), override=True)
    # set loguru
    logger.add(Mytube.LOGFILE.value, rotation="10 MB")

    filename = ""
    st.set_page_config("MyTube", layout=Mytube.LAYOUT.value)

    st.title(Mytube.TITLE.value)
    "이 사이트는 입력된 유튜브 비디오를 저장해서 사용자에게 다운로드 해줘요 ;)"

    with st.form("myform"):
        yt_url = st.text_input(Mytube.LABEL.value, max_chars=200, key="myurl")
        submitted = st.form_submit_button("Submit")

        if submitted and yt_url:
            # st.write(f"Submitted url is {yt_url}")
            logger.info(f"URL: {yt_url}")
            if filename := download_yt(url=yt_url):
                st.success("Finish downloading.")

    if filename:
        with st.empty():
            with open(filename, "rb") as file:
                st.download_button(
                    label="Download file",
                    data=file,
                    file_name=filename,
                    mime="video/mp4",
                    on_click=delete_downloaded_file,
                    args=(filename,),
                )
