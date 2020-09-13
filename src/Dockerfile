FROM python:3.8 as builder
WORKDIR /workspace/konoha
RUN apt update -y && \
    apt upgrade -y
COPY ./app/Pipfile ./app/Pipfile.lock /workspace/konoha/
RUN pip install pipenv && \
    pipenv install --system

FROM python:3.8-slim
WORKDIR /workspace/konoha
RUN apt update -y && \
    apt upgrade -y && \
    apt install -y nodejs npm curl && \
    npm install -g n && \
    n stable && \
    apt purge -y nodejs npm && \
    apt install -y ffmpeg && \
    apt autoremove -y
RUN npm install -g nodemon
ENV PYTHONBUFFERED=1

WORKDIR /workspace/
RUN apt -y install open-jtalk open-jtalk-mecab-naist-jdic wget unzip
RUN wget https://sourceforge.net/projects/mmdagent/files/MMDAgent_Example/MMDAgent_Example-1.6/MMDAgent_Example-1.6.zip/download -O MMDAgent_Example-1.6.zip && \
    unzip MMDAgent_Example-1.6.zip MMDAgent_Example-1.6/Voice/* && \
    mkdir /usr/share/hts-voice && \
    cp -r MMDAgent_Example-1.6/Voice/mei/ /usr/share/hts-voice

RUN apt install -y mecab libmecab-dev mecab-ipadic-utf8 make sudo git xz-utils file
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git && \
    cd mecab-ipadic-neologd && \
    bin/install-mecab-ipadic-neologd -n -y

WORKDIR /workspace/konoha

COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY . /workspace/konoha
RUN pip uninstall -y uvicorn
RUN pip install uvicorn mecab-python3
RUN sed -i -e 's|dicdir = /var/lib/mecab/dic/debian|dicdir = /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd|' /etc/mecabrc && \
    cp /etc/mecabrc /usr/local/etc
# '-d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd'

COPY ipaexg.ttf /usr/share/fonts/truetype
RUN echo 'font.family : IPAexGothic' >> /usr/local/lib/python3.8/site-packages/matplotlib/mpl-data/matplotlibrc && \
    rm -rf /root/.config/matplotlib

