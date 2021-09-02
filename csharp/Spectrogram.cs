using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class Spectrogram: MonoBehaviour
{
    static List<Fingerprint> music_list;
    static List<(int, int)> record_max;

    [System.Serializable]
    public class Fingerprint
    {
        public string title;
        public List<(int, int)> max_values;
    }

    public static string Search(AudioSource aud)
    {
        BinaryFormatter bf = new BinaryFormatter();
#if UNITY_EDITOR
        string path = Application.streamingAssetsPath + "/out_fingerprint/fingerprints.txt";
        FileStream file = File.Open(path, FileMode.Open);
#elif UNITY_ANDROID
        string path = "jar:file://" + Application.dataPath + "!/assets/out_fingerprint/fingerprints.txt";
        UnityWebRequest www = UnityWebRequest.Get(path);
        www.SendWebRequest();
        while (!www.downloadHandler.isDone) { }
        MemoryStream file = new MemoryStream(www.downloadHandler.data);
#elif UNITY_IOS
        string path = Application.dataPath + "/Raw/out_fingerprint/fingerprints.txt";
        MemoryStream file = new MemoryStream(System.IO.File.ReadAllBytes(path));
#endif
        if (file != null && file.Length > 0)
        {
            List<Fingerprint> data = (List<Fingerprint>)bf.Deserialize(file);
            music_list = data;
        }
        file.Close();

        record_max = ParseFingerprint(aud, true);

        /*foreach ((int, int) item in record_max)
        {
            Debug.Log("(" + item.Item1 + "," + item.Item2 + ")");
        }*/
        Debug.Log(record_max.Count);

        foreach (Fingerprint fp in music_list)
        {
            Debug.Log("title: " + fp.title);
            List<(int, int)> max_values = fp.max_values;
            /*foreach ((int, int) item in max_values)
            {
                Debug.Log("(" + item.Item1 + "," + item.Item2 + ")");
            }
            Debug.Log(max_values.Count);*/
            Dictionary<int, int> delta = new Dictionary<int, int>();
            for (int i = 0; i < max_values.Count; i++)
            {
                /*int index_target = i;
                int index_record = 0;
                int count = 0;*/
                for (int j = 0; j < record_max.Count; j++)
                {
                    if (max_values[i].Item1 == record_max[j].Item1)
                    {
                        int temp = max_values[i].Item2 - record_max[j].Item2;

                        if (delta.ContainsKey(temp))
                        {
                            delta[temp]++;
                        }
                        else
                        {
                            delta.Add(temp, 1);
                        }
                    }
                }
                    /*while (index_record < record_max.Count && index_target < max_values.Count)
                    {
                        if (max_values[index_target].Item1 == record_max[index_record].Item1)
                        {
                            int temp = max_values[index_target].Item2 - record_max[index_record].Item2;

                            if (delta.ContainsKey(temp)) {
                                delta[temp]++;
                            } else {
                                delta.Add(temp, 1);
                            }

                            count++;
                            index_target++;
                            index_record++;

                            continue;
                        }

                        if (max_values[index_target].Item1 > record_max[index_record].Item1)
                        {
                            index_record++;
                        }
                        else
                        {
                            index_target++;
                        }

                        if (index_record > 10 && index_target - i > 10 && Math.Max((float)count / index_record, (float)count / (index_target - i)) < 0.3f)
                        {
                            break;
                        }
                    }*/

                /*int max = 0;
                for (int j = 0; j < delta.Count; j++) {
                    max = Math.Max(max, delta.Values.ToList()[j]);
                }

                if (index_record > 10 && index_target - i > 10 && Math.Max((float)max / index_record, (float)max / (index_target - i)) > 0.6f) {
                    Debug.Log(max);
                    Debug.Log(index_record);
                    Debug.Log(index_target - i);
                    return fp.title + "\n" + (Math.Max((float)max / index_record, (float)max / (index_target - i)) * 100).ToString("F2") + "%";
                }*/
            }
            int max = 0;
            var keys = delta.Keys.ToList();
            foreach (int item in keys)
            {
                if (max < delta[item]) {
                    max = delta[item];
                }
            }
            /*Debug.Log(max);
            Debug.Log(record_max.Count);*/
            /*Debug.Log((float)max / (end_index - start_index + 1));*/
            // return fp.title + "\nmax: " + max + "\n" + ((float)max / (end_index - start_index + 1) * 100).ToString("F2") + "%";
            Debug.Log(max);
            if (max > 39 && (float)max / record_max.Count >= 0.3f)
            {
                return fp.title + "\nmax: " + max + "\n" + ((float)max / record_max.Count * 100).ToString("F2") + "%";
            }
        }

        /*foreach (Fingerprint fp in music_list)
        {
            float max = 0f;
            Debug.Log("title: " + fp.title);
            List<(int, int)> max_values = fp.max_values;

            int time = -1;
            for (int i = 4 * 10; i < max_values.Count; i++)
            {
                if (max_values[i].Item2 != time) {
                    time = max_values[i].Item2;
                    int index_record = 0;
                    int index_target = i;
                    int delta = -1;
                    int count = 0;
                    for (int j = 0; j < 4 * 10; j++) {
                        if (max_values[i].Item1 == record_max[j].Item1) {
                            delta = max_values[i].Item2 - record_max[j].Item2;
                            break;
                        }
                    }

                    if (delta == -1) {
                        continue;
                    }

                    
                    while (index_record < record_max.Count && index_target < max_values.Count)
                    {
                        if (max_values[index_target].Item2 - record_max[index_record].Item2 == delta)
                        {
                            if (max_values[index_target].Item1 == record_max[index_record].Item1)
                            {
                                count++;
                                index_target++;
                                index_record++;
                                continue;
                            }

                            if (max_values[index_target].Item1 > record_max[index_record].Item1)
                            {
                                index_record++;
                            }
                            else
                            {
                                index_target++;
                            }
                        }
                        else if (max_values[index_target].Item2 - record_max[index_record].Item2 > delta)
                        {
                            index_record++;
                        }
                        else
                        {
                            index_target++;
                        }

                        if (index_record > 4 * 10 && index_target > i && (float)count / (index_target - i) < 0.2f)
                        {
                            break;
                        }
                    }

                    if (index_record > 4 * 10 && index_target > i && (float)count / (index_target - i) > 0.5f) {
                        max = Math.Max(max, (float)count / (index_target - i));
                    }

                }

            }

            if (max > 0.5f) {
                return fp.title + "\n" + max * 100 + "%";
            }
        }*/

        return "매칭 실패"; // 곡 이름과 매칭률 퍼센티지 출력, 매칭이 안 되었을 경우 "" 출력
    }

    public void Convert() {
#if UNITY_EDITOR
        StartCoroutine(MakeFingerprint());
#endif
    }
    public IEnumerator MakeFingerprint() {
        yield return StartCoroutine(GetAudioClips());
    }
    public IEnumerator GetAudioClips()
    {
        music_list = new List<Fingerprint>();
        string path = Application.streamingAssetsPath + "/in_music";
        string[] files = Directory.GetFiles(path);
        AudioSource aud = GetComponent<AudioSource>();

        foreach (string file in files)
        {
            string[] name = file.Split('.');
            string extension = name[name.Length - 1];

            if (extension != "wav" && extension != "mp3")
            {
                yield return null;
            }
            else {
                using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(file.Replace("\\", "/"), extension == "wav" ? AudioType.WAV : AudioType.MPEG)) {
                    yield return www.SendWebRequest();

                    if (!www.isDone) // www.result == UnityWebRequest.Result.ConnectionError
                    {
                        Debug.Log(www.error);
                    }
                    else
                    {
                        aud.clip = DownloadHandlerAudioClip.GetContent(www);
                        Fingerprint fp = new Fingerprint();
                        string[] temp = file.Replace("\\", "/").Split('/');
                        fp.title = temp[temp.Length - 1];
                        fp.max_values = ParseFingerprint(aud);
                        Debug.Log(fp.max_values.Count);
                        music_list.Add(fp);
                    }
                }
            };
        }

        // arr를 적절히 변환하여 fingerprint에 넣기 (file + ".txt"). RIde and Run 코드 참조
        BinaryFormatter bf = new BinaryFormatter();
        FileStream local_file = File.Create(Application.streamingAssetsPath + "/out_fingerprint/fingerprints.txt");

        bf.Serialize(local_file, music_list);
        local_file.Close();
        Debug.Log("Done");
    }

    public static void FFT(Complex[] data, out Complex[] result) {
        int n = data.Length;
        result = new Complex[n];
        if (n == 1)
        {
            result[0] = data[0];
            return;
        }
        Complex[] even = new Complex[n / 2], odd = new Complex[n / 2], Even = new Complex[n / 2], Odd = new Complex[n / 2];
        for (int i = 0; i < n / 2; i++)
        {
            even[i] = data[2 * i];
            odd[i] = data[2 * i + 1];
        }
        FFT(even, out Even);
        FFT(odd, out Odd);
        double th = -2.0 * Math.PI / n;
        Complex w = new Complex(Math.Cos(th), Math.Sin(th));
        Complex z = Complex.One;
        for (int i = 0; i < n / 2; i++)
        {
            result[i] = Even[i] + z * Odd[i];
            result[i + n / 2] = Even[i] - z * Odd[i];
            z *= w;
        }
    }

    // record의 경우는 각 샘플 당 4개씩 저장 (노이즈 등 포함), 일반 노래의 경우 조건에 맞는 것들만 저장
    public static List<(int, int)> ParseFingerprint(AudioSource aud, bool record = false)
    {
        int freq = aud.clip.frequency;
        Debug.Log("freq: " + freq);
        float[] samples_total = new float[aud.clip.samples * aud.clip.channels];

        aud.clip.GetData(samples_total, 0);

        if (aud.clip.channels != 1) {
            float[] temp = new float[aud.clip.samples];
            for (int i = 0; i < aud.clip.samples; i++) {
                for (int j = 0; j < aud.clip.channels; j++) {
                    temp[i] += samples_total[i * aud.clip.channels + j];
                }
                temp[i] /= aud.clip.channels;
            }
            samples_total = temp;
        }

        int num = Get2Power(freq); // 11025Hz로 샘플링된 파일
        if (freq != 11025 && freq != 22050 && freq != 44100 && freq != 88200)
        {
            Debug.Log("The frequency isn't in (11025Hz, 22050Hz, 44100Hz, 88200Hz).");
            // 44100으로 변환
            if (freq < 44100)
            {

            }
            else
            {

            }
        }

        // float low_sum = 0f;
        List<float[]> vs = new List<float[]>(); // for fingerprint
        List<(int, int)> arr = new List<(int, int)>(); // index, time

        for (int i = 0, k = 0; i + num - 1 < samples_total.Length; i += num, k++)
        {
            float[] result = new float[512]; // 512개만 뽑기
            Split(samples_total, i, num, out float[] samples);
            Complex[] trans = new Complex[num];

            for (int j = 0; j < num; j++) {
                trans[j] = samples[j] * (0.54 + 0.46 * Math.Cos(2 * Math.PI * j / num)); // hamming window function 추가
            }

            FFT(trans, out Complex[] outputs);

            float max = (float)outputs[0].Magnitude;
            for (int j = 0; j < (record ? 200 : result.Length); j++)
            {
                result[j] = (float)outputs[j].Magnitude;
                /*if (j < 48 && max < (float)outputs[j].Magnitude)
                {
                    max = (float)outputs[j].Magnitude;
                }*/
                max = Math.Max(max, (float)outputs[j].Magnitude);
            }
            // low_sum += max;

            if (max < 0.1f) { continue; } // 너무 작은 경우 패스

            for (int j = 0; j < (record ? 200 : result.Length); j++)
            {
                if (result[j] > max * (record ? 0.7f : 0.5f))
                {
                    arr.Add((j, k));
                }
            }
        }

        /*float low_ave = low_sum / vs.Count;

        for (int i = 0; i < vs.Count; i++)
        {
            for (int j = 0; j < vs[i].Length; j++)
            {
                if (vs[i][j] > low_ave * 1.2f)
                {
                    arr.Add((j, i));
                }
            }
        }*/

        return arr;
    }

    public static int Get2Power(int freq) { 
        if (freq == 11025) { return 1024; }
        if (freq == 22050) { return 2048; }
        if (freq == 88200) { return 8192; }

        return 4096;
    }

    public static void Split<T>(T[] array, int index, int number, out T[] first)
    {
        first = array.Skip(index).Take(number).ToArray();
    }
}
