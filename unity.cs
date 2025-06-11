using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using System.IO;
using System.Collections;

public class VRTeacherController : MonoBehaviour
{
    [Header("ネットワーク設定")]
    public int imagePort = 12346;
    public int audioPort = 12347;
    
    [Header("UI要素")]
    public RawImage kokubanImage;
    public Text jishiText;
    public AudioSource voiceAudioSource;
    public Animator senseiAnimator;
    
    [Header("表示設定")]
    public float jishiFadeTime = 0.5f;
    public float imageTransitionTime = 0.3f;
    
    // プライベート変数
    private UdpClient imageUdpClient;
    private UdpClient audioUdpClient;
    private Thread imageReceiveThread;
    private Thread audioReceiveThread;
    private bool isReceiving = true;
    
    // 画像処理用
    private Queue<byte[]> imageQueue = new Queue<byte[]>();
    private object imageLock = new object();
    
    // 音声処理用
    private Queue<string> audioQueue = new Queue<string>();
    private object audioLock = new object();
    
    // UI状態管理
    private bool isJishiVisible = false;
    private Coroutine jishiFadeCoroutine;
    private Coroutine imageTransitionCoroutine;
    
    // アニメーション制御
    private bool isSenseiSpeaking = false;
    private float lastSpeechTime;
    
    void Start()
    {
        StartUdpListeners();
        InitializeUI();
        LogMessage("VR先生システム初期化完了");
    }
    
    void StartUdpListeners()
    {
        try
        {
            // 画像受信用UDP
            imageUdpClient = new UdpClient(imagePort);
            imageReceiveThread = new Thread(ReceiveImageData);
            imageReceiveThread.IsBackground = true;
            imageReceiveThread.Start();
            
            // 音声受信用UDP
            audioUdpClient = new UdpClient(audioPort);
            audioReceiveThread = new Thread(ReceiveAudioData);
            audioReceiveThread.IsBackground = true;
            audioReceiveThread.Start();
            
            LogMessage($"UDP受信開始 - 画像ポート:{imagePort}, 音声ポート:{audioPort}");
        }
        catch (Exception e)
        {
            LogMessage($"UDP初期化エラー: {e.Message}");
        }
    }
    
    void InitializeUI()
    {
        if (jishiText != null)
        {
            jishiText.color = new Color(jishiText.color.r, jishiText.color.g, jishiText.color.b, 0f);
            jishiText.text = "";
        }
        
        if (kokubanImage != null)
        {
            kokubanImage.color = Color.white;
        }
        
        if (senseiAnimator != null)
        {
            senseiAnimator.SetBool("IsSpeaking", false);
            senseiAnimator.SetBool("IsTeaching", false);
        }
    }
    
    void ReceiveImageData()
    {
        IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, imagePort);