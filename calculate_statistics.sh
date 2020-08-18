n_complex_sent=$(grep -o "sent_id" output_test_complex.txt | wc -l)
n_simple_sent=$(grep -o "sent_id" output_test_simple.txt | wc -l)
n_simple_doc=$(grep -o "newdoc" output_test_simple.txt | wc -l)
n_complex_doc=$(grep -o "newdoc" output_test_complex.txt | wc -l)
n_simple_par=$(grep -o "newpar" output_test_simple.txt | wc -l)
n_complex_par=$(grep -o "newpar" output_test_complex.txt | wc -l)
file_length_complex=$(wc -l output_test_complex.txt| awk '{ print $1 }')
file_length_simple=$(wc -l output_test_simple.txt | awk '{ print $1 }')
n_complex_token=$(($file_length_complex - $n_complex_doc - $n_complex_par - $((3*$n_complex_sent))))
n_simple_token=$(($file_length_simple - $n_simple_doc - $n_simple_par - $((3*$n_simple_sent))))

echo "\tdocs\tpars\tsents\ttokens"
echo "simple\t$n_simple_doc\t$n_simple_par\t$n_simple_sent\t$n_complex_token"
echo "complex\t$n_complex_doc\t$n_complex_par\t$n_complex_sent\t$n_simple_token"
