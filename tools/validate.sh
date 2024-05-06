#write a tool to validate the input using the module yamale
#yamale is a schema and validator for YAML.
#It defines a standard way to describe the format of a YAML file and validate it.
#It is based on the PyYaml library.
#The goal is to specify the schema of the YAML file you use, load it, and then validate the content of the file against the schema.
#The schema is described in a YAML file.
#The content of the file is also described in a YAML file.
#The schema and the content are then loaded and validated by yamale.
#!/usr/bin/sh
Help()
{
   # Display Help
   echo
   echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   echo " running yamale tool to validate the input using the module yamale"
   echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   echo
   echo "Syntax: validate.sh [-sdh]"
    echo "options:"
    echo " -h     Print this Help."
    echo " -s     schema file"
    echo " -d     data file"
   echo "Example: ./tools/validate.sh -s schema.yaml -d data.yaml"
}
yamaleOptions=""
while getopts "s:d:h" option; do
    case $option in
        h) # display Help
            Help
            #exit
            ;;
        s) # schema file
            echo $OPTARG
            yamaleOptions="${yamaleOptions} -s ${OPTARG}"
            ;;
        d) # data file
            echo $OPTARG
            yamaleOptions="${yamaleOptions}  ${OPTARG}"
            ;;
        \?) # Invalid option
            echo "Error: Invalid option"
            #exit
            ;;
    esac
done
if [ -z "$yamaleOptions" ]; then
    echo "Error: Missing required options"
    Help
    exit 1
fi
echo "yamale  $yamaleOptions"
yamale  $yamaleOptions

