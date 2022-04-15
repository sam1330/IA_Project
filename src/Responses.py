from datetime import datetime

def sample_responses(input_text):
  user_message = input_text.lower()

  if user_message in ['hi', 'hello', 'hey']:
    return 'Hello!'

  if user_message in ['how are you', "how's it going", 'how are you doing']:
    return 'Im good, how about you?'

  if user_message in ['time', 'time?']:
    now = datetime.now()
    date_time = now.strftime("%d/%m/%y, %H:%M:%S")

    return 'The time is ' + date_time

  if user_message in ['mariana', 'marianita']:
    return 'I love you, Mariana!. from your love Samuel'

  return 'I dont understand you'