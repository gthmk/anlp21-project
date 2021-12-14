This directory contains the code for INFO 256 - ANLP21 project by Pratik Aher, Romit Barua, and Gautham Koorma.

We genrated features from song lyrics and chord progressions and used the features in a random forest regressor to predict musical attribute scores provided by Spotify (danceability, acousticness, valence, energy).

The Pipeline folder contains the main pipeline for running the experiment.

## Summary of folders

| Directory | Summary |
|---|---|
| ChordsAndTabs | Contains code for the ultimate guitar scraper and inital chordcaster  |
| EDA | SNS plots for the Spotify data |   
| Embeddings | Inital experimen with creating word2vec embeddings  |   
| Emotion | Deriving sentiment features from lyrics |
| LDA | Topic Modeling using gensim with coherence tests |
| Pipeline | Final pipeline for running experiments |
| genius_lyrics | Script for pulling songs from genius API |
