from agile import AgileManager

app_module = 'agile'

if __name__ == '__main__':
    AgileManager(description='Release manager for pulsar-agile',
                 config='agileplay.py').start()
