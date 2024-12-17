import os

dir = "data/test02/mbd/"
outdir = "data/test02/mbd/clipped/"

for updir in os.listdir(dir):
    if updir.endswith(".txt"):
        continue
    if os.path.basename(updir) == "clipped":
        continue
    txtFile = updir + ".txt"
    fid = open(dir + txtFile, 'r')
    clipTime = float(fid.readline())
    fid.close()

    for inputFile in os.listdir(dir + updir):
        print(clipTime)
        inFile = dir + updir + "/" + inputFile
        # create output
        if not os.path.isdir(outdir + updir):
            os.mkdir(outdir + updir)
        outFile = outdir + updir + "/" + inputFile
        print(outFile)
        if os.path.isfile(outFile):
            os.remove(outFile)

        inData = open(inFile, 'r')
        outData = open(outFile, 'a+')

        for line in inData:
            splitted = line.strip().split(',')
            if splitted[0] == '':
                continue
            print(splitted[0], clipTime)

            if float(splitted[0]) >= clipTime:
                outData.write(line)

