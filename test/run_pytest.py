import os


def rm_pyc():
    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for root, dirs, files in os.walk(project_folder, topdown=False):
        for name in files:
            file = os.path.join(root, name)
            if file.endswith(".pyc"):
                print(file)
                os.remove(file)


if __name__ == '__main__':
    import sys
    rm_pyc()
    list_of_arguments = sys.argv[1:]
    os.system(f"pytest --cache-clear -v --cov=apis "
              f"{'.' if not list_of_arguments else ' '.join(list_of_arguments)}")
    # 执行所有测试 python test/run_pytest.py
    # 只执行某个模块 python test/run_pytest.py test/test_model
    # 只执行某个文件测试 python test/run_pytest.py test/test_model/test_xx_model.py
    # 只执行某个func  python test/run_pytest.py test/test_model/test_xx_model.py::TestClsModel::test_v0_xx_func
