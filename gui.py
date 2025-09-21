from nicegui import ui
import main

# def main_loop_step():
#     desired = input("Enter desired note (E2-E4): ") 
#     main.main()




record = False
def toggle_record():
    global record
    record = not record
    print(record)
    record_button.set_text('Stop' if record else 'Record')
    if record:
        main.main()
    else:
        main.stop()
    
        
record_button = ui.button('Record', on_click=lambda: toggle_record())

# while True:
#     if record:
ui.run()

# main.main()
