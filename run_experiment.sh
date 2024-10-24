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

###### installation
#conda create --name UUParser python=3.7
#conda install numpy=1.16.1
#conda install cython
#pip install dynet==2.1
#conda install h5py=2.9.0
#conda list --export | tee UUParser_packagelist.txt
###########

conda activate UUParser

##### train the parser


INCLUDE=$1 # "${ARMENIAN}"
SEED=$2
COMPOSITION=$3 #0 1 2 3
CROFTIZE=$4
RANDOMIZED=$5

UDVER=v2.12
EPOCHS=30
DATADIR=/work/Home/data/ud-treebanks-${UDVER}
OUTDIR=models/$UDVER/${INCLUDE}_CMP${COMPOSITION}_EPC${EPOCHS}_SD${SEED}_CROFT${CROFTIZE}_RAND${RANDOMIZED}
PARSER=src/parser.py

echo $DATADIR $INCLUDE

if [ $CROFTIZE -eq 1 ]
then
for file in $(find $DATADIR -name ${INCLUDE}-ud*.conllu)
do
	echo "test the existence of ${file}.croft"
	if [ ! -f ${file}.croft ]
	then
	echo "croftizing $file"
	python croftizer_new.py $file $file.croft
	fi
done
fi

if [ $RANDOMIZED -eq 1 ]
then
	echo "start randomization ..."
	random_suffix=randchange_s$SEED

        train_corpus=$(find $DATADIR -name ${INCLUDE}-ud-train.conllu)
        dev_corpus=$(find $DATADIR -name ${INCLUDE}-ud-dev.conllu)
        test_corpus=$(find $DATADIR -name ${INCLUDE}-ud-test.conllu)

        train_corpus_random=${train_corpus}.${random_suffix}
        dev_corpus_random=${dev_corpus}.${random_suffix}
        test_corpus_random=${test_corpus}.${random_suffix}

        echo $train_corpus $train_corpus_random
        python random_rule_generator_simulated_annealing.py ${train_corpus} ${dev_corpus} ${test_corpus} \
            ${train_corpus_random} ${dev_corpus_random} ${test_corpus_random} \
            ${random_model}.rule_log

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
	--randomized $RANDOMIZED \
	--epochs $EPOCHS #> ${OUTDIR}/train.log

#python  $PARSER --outdir ${OUTDIR} --datadir ${DATADIR} \
#	--graph-based \
#	--include $INCLUDE \
#	--char-emb-size 100 --char-lstm-output-size 100 --word-emb-size 100 \
#	--lstm-output-size 125 --no-bilstms 2 \
#	--dynet-seed $SEED --dynet-mem 1000 \
#	--croftize $CROFTIZE \
#	--epochs $EPOCHS #> ${OUTDIR}/train.log


conda deactivate

