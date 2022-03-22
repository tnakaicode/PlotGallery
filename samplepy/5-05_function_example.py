def function_a():
    print('function_aの処理です')

def function_b():
    print('function_b の処理開始')
    function_a()
    print('function_bの処理終了')

print('function_bを呼び出します')
function_b()
