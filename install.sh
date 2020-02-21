conda create -n mowgli-env python=3.6 anaconda
source activate mowgli-env

git clone https://github.com/ucinlp/mowgli-uci.git
cd mowgli-uci
pip install -r requirements.txt
conda install --yes faiss-cpu -c pytorch
python -m spacy download en_core_web_lg

curl https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-en-19.08.txt.gz --output numberbatch-en-19.08.txt.gz
gunzip numberbatch-en-19.08.txt.gz
cd ..

pip install -r requirements.txt
