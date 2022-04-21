import random
import time

import speech_recognition as sr


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    从 "麦克风 "记录的语音中转录。
    返回一个有三个键的字典：
    "success": 一个布尔值，表示API请求是否成功
    "error":   `None`，如果没有发生错误，
               否则是一个字符串，包含错误信息，如果不能到达API或语音无法辨认
    "transcription": `None`如果语音不能被转录。
               否则是一个包含转录文本的字符串
    """
    
    # check that recognizer and microphone arguments are appropriate type检查识别器和麦克风的参数是否为适当的类型
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone调整识别器对环境噪音的敏感度，并从麦克风录制音频
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object设置响应对象
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    # 如果捕捉到RequestError或UnknownValueError异常，
    # 尝试识别录音中的语音。 相应地更新响应对象
    try:
        response["transcription"] = recognizer.recognize_sphinx(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive API无法访问或无响应
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible 说话不知所云
        response["error"] = "Unable to recognize speech"

    return response


if __name__ == "__main__":
    # set the list of words, maxnumber of guesses, and prompt limit设置单词列表、最大猜测数和提示限制
    WORDS = ["apple", "banana", "grape", "orange", "mango", "lemon"]
    NUM_GUESSES = 3
    PROMPT_LIMIT = 5

    # create recognizer and mic instances创建识别器和麦克风实例
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # get a random word from the list从列表中获得一个随机的词
    word = random.choice(WORDS)

    # format the instructions string格式化指示字符串
    instructions = (
        "I'm thinking of one of these words:\n"
        "{words}\n"
        "You have {n} tries to guess which one.\n"
    ).format(words=', '.join(WORDS), n=NUM_GUESSES)

    # show instructions and wait 3 seconds before starting the game 显示指示并等待3秒后开始游戏
    print(instructions)
    time.sleep(3)

    for i in range(NUM_GUESSES):
        # get the guess from the user从用户那里得到猜测的结果
        # if a transcription is returned, break out of the loop and如果返回的是转述，则跳出循环并继续
        #     continue
        # if no transcription returned and API request failed, break如果没有返回转录，且API请求失败，则脱离循环并继续循环并继续
        #     loop and continue
        # if API request succeeded but no transcription was returned,如果API请求成功了，但没有返回转录。
        #     re-prompt the user to say their guess again. Do this up
        #     to PROMPT_LIMIT times重新提示用户再次说出他们的猜测。做到这一点 到PROMPT_LIMIT次数
        for j in range(PROMPT_LIMIT):
            print('Guess {}. Speak!'.format(i+1))
            guess = recognize_speech_from_mic(recognizer, microphone)
            if guess["transcription"]:
                break
            if not guess["success"]:
                break
            print("I didn't catch that. What did you say?\n")

        # if there was an error, stop the game如果有错误，就停止游戏
        if guess["error"]:
            print("ERROR: {}".format(guess["error"]))
            break

        # show the user the transcription向用户展示转录的内容
        print("You said: {}".format(guess["transcription"]))

        # determine if guess is correct and if any attempts remain确定猜测是否正确以及是否还有任何尝试
        guess_is_correct = guess["transcription"].lower() == word.lower()
        user_has_more_attempts = i < NUM_GUESSES - 1

        # determine if the user has won the game确定用户是否已经赢得游戏
        # if not, repeat the loop if user has more attempts 如果没有，如果用户有更多的尝试，就重复这个循环
        # if no attempts left, the user loses the game 如果没有尝试了，用户就输掉了游戏
        if guess_is_correct:
            print("Correct! You win!".format(word))
            break
        elif user_has_more_attempts:
            print("Incorrect. Try again.\n")
        else:
            print("Sorry, you lose!\nI was thinking of '{}'.".format(word))
            break