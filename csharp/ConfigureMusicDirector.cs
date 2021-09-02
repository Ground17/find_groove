using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System.Net;
using System.IO;
using static System.Net.WebRequestMethods;
using System.Net.Sockets;

public class ConfigureMusicDirector : MonoBehaviour
{
    public ParticleSystem ps;
    public GameObject button;
    public Text text;
    public Sprite start;
    public Sprite pause;
    public bool Make_Fingerprint; // check to make fingerprint (only works on editor)
    bool listening;

    bool local;
    bool ai;

    AudioSource aud;
    private string url;

    [System.Serializable]
    public class InData {
        public List<float> samples;
        public bool ai;
    }

    [System.Serializable]
    public class OutData
    {
        public string code;
        public string message;
    }

    // Start is called before the first frame update
    void Start()
    {
        local = false;
        ai = false;
        aud = GetComponent<AudioSource>();

#if UNITY_EDITOR
        if (Make_Fingerprint)
        {
            Spectrogram sp = GetComponent<Spectrogram>();
            sp.Convert(); // Editor에서만 실행하여 fingerprint 파일 생성
        }
#endif

        listening = false;
        text.text = "Press start to listen."; // LocalizationManager.instance.GetLocalizedValue("pauseMusic");
        button.GetComponent<Image>().sprite = start;
        ps.Stop();

        StartCoroutine(Listen());
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
                aud.clip = Microphone.Start(null, false, 4, 11025);
                Invoke("Pause", 4f);
            }
        }
        else
        {
            Debug.Log("Microphone not found");
        }
    }

    public static string LocalIPAddress()
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
    }

    void Pause()
    {
        listening = false;
        text.text = Make_Fingerprint ? "" : "처리중입니다..."; // LocalizationManager.instance.GetLocalizedValue("pauseMusic");
        button.GetComponent<Image>().sprite = start;
        ps.Stop();

        if (!Make_Fingerprint && aud.clip != null && aud.clip.length > 1.9f)
        {
            LocalIPAddress();
            text.text = Spectrogram.Search(aud);
            float[] samples = new float[aud.clip.samples];
            aud.clip.GetData(samples, 0);

            InData inData = new InData();
            inData.samples = new List<float>(samples);
            inData.ai = ai;

            string str = JsonUtility.ToJson(inData);
            var bytes = System.Text.Encoding.UTF8.GetBytes(str);

            Debug.Log(local ? "http://" + LocalIPAddress() + ":8080/search" : "https://focused-code-322801.du.r.appspot.com/search");
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(local ? "http://" + LocalIPAddress() + ":8080/search" : "https://focused-code-322801.du.r.appspot.com/search");
            
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

            Debug.Log(outData.message);
            // text.text = outData.message;
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
    public void Toggle1(bool changed)
    {
        ai = changed;
    }

    public void Open()
    {
        // LoadingSceneManager.LoadScene("00Open");
    }
}
