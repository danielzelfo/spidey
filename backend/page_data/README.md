create tar file part files
```
tar -cvzf - data/* | split -b 50M - "data.tar.gz-part"
```

join tar files
```
cat data.tar.gz-part* > data.tar.gz
```