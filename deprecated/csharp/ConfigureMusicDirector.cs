using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System.Net;
using System.IO;
using System.Net.Sockets;
using UnityEngine.Networking;

public class ConfigureMusicDirector : MonoBehaviour
{
    public ParticleSystem ps;
    public GameObject button;
    public GameObject popup;
    public Text text;
    public Text explanation;
    public Text title;
    public Text recommend1text;
    public Text recommend2text;
    public Text recommend3text;
    public GameObject smallPlay;
    public GameObject smallPlay1;
    public GameObject smallPlay2;
    public GameObject smallPlay3;
    public Text lengthText;
    public Sprite start;
    public Sprite pause;
    public bool Make_Fingerprint; // check to make fingerprint (only works on editor)
    bool listening;

    bool local;
    int length;

    AudioSource aud;
    private string url;

    [System.Serializable]
    public class InData {
        public List<float> samples;
    }

    [System.Serializable]
    public class OutData
    {
        public string name; // 찾은 음원
        public string recommend1; // 추천 음원 1
        public string recommend2; // 추천 음원 2
        public string recommend3; // 추천 음원 3
        public float accuracy; // 정확도
        public float time; // 걸린 시간
    }

    // Start is called before the first frame update
    void Start()
    {
        local = true;
        length = 3;
        lengthText.text = "녹음시간: " + length.ToString() + "초";
        aud = GetComponent<AudioSource>();
        popup.SetActive(false);

#if UNITY_EDITOR
        if (Make_Fingerprint)
        {
            Spectrogram sp = GetComponent<Spectrogram>();
            sp.Convert(); // Editor에서만 실행하여 fingerprint 파일 생성
        }
#endif

        listening = false;
        text.text = "시작을 눌러 음악을 듣습니다."; // LocalizationManager.instance.GetLocalizedValue("pauseMusic");
        button.GetComponent<Image>().sprite = start;
        ps.Stop();

        // StartCoroutine(Listen());
    }

    /*// Update is called once per frame
    void Update()
    {
        
    }*/

    IEnumerator Listen()
    {
        yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);
        if (Application.HasUserAuthorization(UserAuthorization.Microphone))
        {
            Debug.Log("Microphone found");

            listening = true;
            text.text = Make_Fingerprint ? "" : "음악을 듣고 있습니다..."; // LocalizationManager.instance.GetLocalizedValue("startMusic");
            button.GetComponent<Image>().sprite = pause;
            ps.Play();

            if (!Make_Fingerprint) {
                // 3초동안 모바일 기기에서 마이크 소리 받기
                aud.clip = Microphone.Start(null, false, length, 11025);
                Invoke("Pause", (float) length);
            }
        }
        else
        {
            Debug.Log("Microphone not found");
        }
    }

    /*public static string LocalIPAddress()
    {
        IPHostEntry host;
        string localIP = "0.0.0.0";
        host = Dns.GetHostEntry(Dns.GetHostName());
        foreach (IPAddress ip in host.AddressList)
        {
            if (ip.AddressFamily == AddressFamily.InterNetwork)
            {
                localIP = ip.ToString();
                break;
            }
        }
        return localIP;
    }*/

    void Pause()
    {
        listening = false;
        text.text = Make_Fingerprint ? "" : "처리중입니다..."; // LocalizationManager.instance.GetLocalizedValue("pauseMusic");
        button.GetComponent<Image>().sprite = start;
        ps.Stop();

        if (!Make_Fingerprint && aud.clip != null && aud.clip.length > length - 0.1f)
        {
            // LocalIPAddress();
            // text.text = Spectrogram.Search(aud);

            aud.Play();
            float[] samples = new float[aud.clip.samples];
            aud.clip.GetData(samples, 0);

            InData inData = new InData();
            inData.samples = new List<float>(samples);

            string str = JsonUtility.ToJson(inData);
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);

            Debug.Log(local ? "http://" + url + ":8080/search" : "https://focused-code-322801.du.r.appspot.com/search");

            try {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(local ? "http://" + url + ":8080/search" : "https://focused-code-322801.du.r.appspot.com/search");

                request.Method = "POST";
                request.ContentType = "application/json";
                request.ContentLength = bytes.Length;
                using (var stream = request.GetRequestStream())
                {
                    stream.Write(bytes, 0, bytes.Length);
                    stream.Flush();
                    stream.Close();
                }

                HttpWebResponse response = (HttpWebResponse)request.GetResponse();
                StreamReader reader = new StreamReader(response.GetResponseStream());
                string json = reader.ReadToEnd();
                OutData outData = JsonUtility.FromJson<OutData>(json);

                popup.SetActive(true);
                text.text = "시작을 눌러 음악을 듣습니다.";
                title.text = outData.name;
                explanation.text = "정확도: " + outData.accuracy * 100 + "%\n소요시간: " + outData.time + "s";
                recommend1text.text = outData.recommend1;
                recommend2text.text = outData.recommend2;
                recommend3text.text = outData.recommend3;
            }
            catch (System.Exception e) {
                text.text = e.ToString();
            }
        }
        else {
            text.text = "녹음이 제대로 이뤄지지 않았습니다.";
        }

    }

    public void ChangeMode() {
        if (!listening)
        {
            StartCoroutine(Listen());
        }
        else {
            Pause();
        }
    }

    public void Toggle(bool changed)
    {
        local = changed;
    }

    public void OK() {
        aud.clip = null;
        smallPlay.GetComponent<Image>().sprite = start;
        smallPlay1.GetComponent<Image>().sprite = start;
        smallPlay2.GetComponent<Image>().sprite = start;
        smallPlay3.GetComponent<Image>().sprite = start;
        popup.SetActive(false);
    }

    public void slider(float changed)
    {
        length = (int) changed;
        lengthText.text = "녹음시간: " + length.ToString() + "초";
    }

    public void InputField(string url) {
        this.url = url;
    }

    public void PlayMusic(int code) {
        switch (code)
        {
            case 1:
                if (smallPlay1.GetComponent<Image>().sprite != start) {
                    aud.Stop();
                    smallPlay1.GetComponent<Image>().sprite = start;
                    return;
                }
                break;
            case 2:
                if (smallPlay2.GetComponent<Image>().sprite != start)
                {
                    aud.Stop();
                    smallPlay2.GetComponent<Image>().sprite = start;
                    return;
                }
                break;
            case 3:
                if (smallPlay3.GetComponent<Image>().sprite != start)
                {
                    aud.Stop();
                    smallPlay3.GetComponent<Image>().sprite = start;
                    return;
                }
                break;
            default:
                if (smallPlay.GetComponent<Image>().sprite != start)
                {
                    aud.Stop();
                    smallPlay.GetComponent<Image>().sprite = start;
                    return;
                }
                break;
        }
        StartCoroutine(GetAudioClip(code));
    }

    public IEnumerator GetAudioClip(int code)
    {
        string playName;
        switch (code)
        {
            case 1:
                playName = recommend1text.text;
                smallPlay1.GetComponent<Image>().sprite = pause;
                break;
            case 2:
                playName = recommend2text.text;
                smallPlay2.GetComponent<Image>().sprite = pause;
                break;
            case 3:
                playName = recommend3text.text;
                smallPlay3.GetComponent<Image>().sprite = pause;
                break;
            default:
                playName = title.text;
                smallPlay.GetComponent<Image>().sprite = pause;
                break;
        }

        string[] temp = playName.Split('.');
        string path = Application.streamingAssetsPath + "/" + temp[0] + "/" + playName + ".wav";

        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(path, AudioType.WAV))
        {
            yield return www.SendWebRequest();

            if (!www.downloadHandler.isDone) // www.result == UnityWebRequest.Result.ConnectionError
            {
                Debug.Log(www.error);
            }
            else
            {
                aud.Stop();
                aud.clip = DownloadHandlerAudioClip.GetContent(www);
                aud.Play();
            }
        }
    }

    public void Open()
    {
        // LoadingSceneManager.LoadScene("00Open");
    }
}
