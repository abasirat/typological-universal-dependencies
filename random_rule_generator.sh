conda_setup() {
	# >>> conda initialize >>>
	# !! Contents within this block are managed by 'conda init' !!
	__conda_setup="$('/work/Home/conda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
	if [ $? -eq 0 ]; then
	    eval "$__conda_setup"
	else
	    if [ -f "/work/Home/conda/etc/profile.d/conda.sh" ]; then
		. "/work/Home/conda/etc/profile.d/conda.sh"
	    else
		export PATH="/work/Home/conda/bin:$PATH"
	    fi
	fi
	unset __conda_setup
	# <<< conda initialize <<<
}
conda_setup


conda activate UUParser

INCLUDE=$1 # "${ARMENIAN}"
SEED=$2
COMPOSITION=$3 #0 1 2 3
CROFTIZE=$4

UDVER=v2.12
EPOCHS=30
DATADIR=/work/Home/data/ud-treebanks-${UDVER}
OUTDIR=models/$UDVER/${INCLUDE}_CMP${COMPOSITION}_EPC${EPOCHS}_SD${SEED}_CROFT${CROFTIZE}
PARSER=src/parser.py

echo $DATADIR $INCLUDE

if [ $CROFTIZE -eq 1 ]
then
for file in $(find $DATADIR -name ${INCLUDE}*.conllu)
do
	echo "test the existence of ${file}.croft"
	if [ ! -f ${file}.croft ]
	then
	echo "croftizing $file"
	python croftizer_new.py $file $file.croft
	fi
done
fi

rm -fr ${OUTDIR}
mkdir -p $OUTDIR


python  $PARSER --outdir ${OUTDIR} --datadir ${DATADIR} \
	--include $INCLUDE \
	--char-emb-size 100 --char-lstm-output-size 100 --word-emb-size 100 \
	--lstm-output-size 125 --no-bilstms 2 \
	--k 2 \
	--disable-rlmost \
	--nucleus-composition $COMPOSITION \
	--dynet-seed $SEED --dynet-mem 1000 \
	--croftize $CROFTIZE \
	--epochs $EPOCHS #> ${OUTDIR}/train.log


conda deactivate
