using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ConfigureMusicDirector : MonoBehaviour
{
    public ParticleSystem ps;
    public GameObject button;
    public Text text;
    public Sprite start;
    public Sprite pause;
    bool listening;

    float[] samples;

    AudioSource aud;

    // Start is called before the first frame update
    void Start()
    {
        aud = GetComponent<AudioSource>();

        listening = false;
        text.text = LocalizationManager.instance.GetLocalizedValue("pauseMusic");
        button.GetComponent<Image>().sprite = start;
        ps.Stop();

        StartCoroutine(Listen());
    }

    // Update is called once per frame
    void Update()
    {
        Debug.Log(samples);
    }

    IEnumerator Listen()
    {
        yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);
        if (Application.HasUserAuthorization(UserAuthorization.Microphone))
        {
            Debug.Log("Microphone found");

            listening = true;
            text.text = LocalizationManager.instance.GetLocalizedValue("startMusic");
            button.GetComponent<Image>().sprite = pause;
            ps.Play();

            // 4초동안 모바일 기기에서 마이크 소리 받기
            aud.clip = Microphone.Start(null, false, 4, 44100);
            Invoke("Pause", 4f);

            // Algorithms.FFT();
        }
        else
        {
            Debug.Log("Microphone not found");
        }
    }

    void Pause()
    {
        listening = false;
        text.text = LocalizationManager.instance.GetLocalizedValue("pauseMusic");
        button.GetComponent<Image>().sprite = start;
        ps.Stop();

        samples = new float[aud.clip.samples * aud.clip.channels];
        aud.clip.GetData(samples, 0);
        aud.Play();
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

    public void Open()
    {
        LoadingSceneManager.LoadScene("00Open");
    }
}
