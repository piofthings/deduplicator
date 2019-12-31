import os
import zlib
import sys, getopt
import logging
import pathlib

class Deduplicator:
    __inputFolder = ''
    __outputFolder = ''
    __originalFolder = ''
    __duplicatesFolder = ''
    __dirCache = dict()
    def __init__(self, argv):
        try:
            opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
            logging.basicConfig(filename='deduper.log',level=logging.INFO)
        except getopt.GetoptError:
            print ('duplicate_files.py -i <inputfile> -o <outputfile>')
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print ('duplicate_files.py -i <inputfile> -o <outputfile>')
                sys.exit()
            elif opt in ("-i", "--ifile"):
                self.__inputFolder = arg.strip()
            elif opt in ("-o", "--ofile"):
                self.__outputFolder = arg.strip()
        print ('Input folder is     :', self.__inputFolder)
        print ('Output folder is    :', self.__outputFolder)
        self.doCompare()


    def find_files(self, url, ext_list):
        result = []
        ext = [x.lower() for x in ext_list]
        for root, dirs, files in os.walk(url):
            for file in files:
                # if file.endswith(ext):
                if file.split('.')[-1].lower() in ext:
                    result.append(os.path.join(root, file))
        return result


    def crc(self, a_file_name):
        prev = 0
        for eachLine in open(a_file_name, "rb"):
            prev = zlib.crc32(eachLine, prev)
        return "%X" % (prev & 0xFFFFFFFF)


    def add_files_to_crc_dict(self, result_dict, file_list):
        ''' Add to the dictionary a list of files that match
            the CRC value. If not already in dictionary, add it.

            dict(){
                [CRC:FILESIZE] : (file1.xyz, file2.xyz...)
                [CRC:FILESIZE] : (file1.xyz, file2.xyz...)
            }
        '''
        for x in file_list:
            dict_index = "{}:{}".format(self.crc(x), os.path.getsize(x))
            try:
                number_of_dups = len(result_dict[dict_index])

                if number_of_dups == 0:
                    print("found zero dups")
                else:
                    result_dict[dict_index].append(x)
            except:
                result_dict[dict_index] = [x]
        return result_dict


    def doCompare(self):
        # Find all files in folder with file extension
        allFiles = self.find_files(self.__inputFolder, ["jpg", "jpeg", "png", "mpg", "mpeg","mov","wmv","avi","mp4","heic","cr2"])
        logging.info("Total     Files %d", len(allFiles))
        print("Total     Files %d", len(allFiles))
        # Create CRC value for each file and add
        # it to the dictionary of combined files
        result_dict = dict()
        result_dict = self.add_files_to_crc_dict(result_dict, allFiles)

        # Find duplicates
        duplicate_filesize = 0
        duplicate_file_count = 0
        for key in result_dict:
            ## Take the file at Index 0 
            ## Create output dir by replacing input dir with output dir (and maintaining the rest of the path)
            ## Do os.replace("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
            self.move_originals(result_dict[key][0])
            self.move_duplicates(result_dict[key][1:])
            num_files = len(result_dict[key])
            if num_files > 1:
                # Duplicate found
                filesize = int(key.split(':')[-1])
                duplicate_filesize += (filesize * (num_files - 1))
                logging.info(key + " : " + str(result_dict[key]))
                duplicate_file_count += 1

        # report how much diskspace will be saved
        print("Duplicate Files %d", duplicate_file_count)
        print("{} MB".format((duplicate_filesize/1024)/1024))
        logging.info("Duplicate Files %d", duplicate_file_count)

    def move_originals(self, file):
        newFileName = file.replace(self.__inputFolder, self.__outputFolder + os.path.sep + "originals" + os.path.sep)
        logging.info("Moving original " + file + " to " + newFileName)

        directory = os.path.dirname(newFileName)
        if(directory not in self.__dirCache):
            self.__dirCache[directory] = "True"
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True) 
        os.rename(file, newFileName) 

    def move_duplicates(self, files):
        for file in files:
            newFileName = file.replace(self.__inputFolder, self.__outputFolder + os.path.sep + "duplicates" + os.path.sep)
            logging.info("Moving duplicate " + file + " to " + newFileName)

            directory = os.path.dirname(newFileName)
            if(directory not in self.__dirCache):
                self.__dirCache[directory] = "True"
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True) 
            os.rename(file ,newFileName)

if __name__ == "__main__":
    dedup = Deduplicator(sys.argv[1:])