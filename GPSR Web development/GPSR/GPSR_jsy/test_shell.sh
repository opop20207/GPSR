timeout 2 ./a.out < io/1/1.in &> user_output.txt
echo $? &> user_error.txt