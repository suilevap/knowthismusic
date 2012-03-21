using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Audio;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.GamerServices;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using Microsoft.Xna.Framework.Media;
using System.IO;

#if WINDOWS_PHONE
using Microsoft.Xna.Framework.Input.Touch;
#endif

namespace WindowsGame1
{
#if !WINDOWS_PHONE
    [Serializable]
#endif
    struct DemoData
    {
        public TimeSpan timeStamp;
        public float[] timePayload;

        public DemoData(TimeSpan _timeStamp, float[] _timePayload)
        {
            timeStamp = _timeStamp;
            timePayload = _timePayload;

        }

    }
    struct DemoData2
    {
        public TimeSpan timeStamp;
        public int index;

        public DemoData2(TimeSpan _timeStamp, int _index)
        {
            timeStamp = _timeStamp;
            index = _index;

        }

    }
    public struct Cursor
    {
        public Vector2 position;
        public Vector2 prevposition;
        public bool pressed;
        public bool justPressed;
        public object draggedObject;
    }

    public struct powerAddition
    {
        public int power;
        public int index;
        public float addition;
        public powerAddition(int power_, float addition_, int index_)
        {
            power = power_;
            addition = addition_;
            index = index_;
        }
    }

    /// <summary>
    /// This is the main type for your game
    /// </summary>
    public class Game1 : Microsoft.Xna.Framework.Game
    {
        GraphicsDeviceManager graphics;
        SpriteBatchEx spriteBatch;
        private List<Texture2D> MelList;
        private Texture2D MouseIcon;
        private Song song;
        private bool PRELOAD = false;
        private bool PRELOAD2 = false;
        private string songFile = "Minus";
        private TimeSpan TimeBetweenWrites = new TimeSpan(200000); // 1/frequency.
        private DateTime startTime; //music start
        private DateTime lastWriteTime;
        private List<MusicSrc> musics = new List<MusicSrc>();
        private SpriteFont font;
#if !WINDOWS_PHONE
        private string demoFile = Directory.GetCurrentDirectory() + "\\demo.txt";
#else
        private string demoFile = "demo.txt";
#endif

        List<DemoData> DemoDatas = new List<DemoData>();
        List<DemoData2> DemoDatas2 = new List<DemoData2>();
        public int demoPointer = 0;
        public int demoPoints;
        float[] visualizationDataMasAvg = new float[128];
        public List<powerAddition> powers = new List<powerAddition>();
        List<string> finalDemo = new List<string>();
        public TimeSpan timeSpa;
        public TimeSpan pogreshn = new TimeSpan(0, 0, 0, 0, 200);
        TimeSpan lastMaxTime = new TimeSpan(0); // mnt. To support prediction functionality
        TimeSpan difficulty = new TimeSpan(0, 0, 0, 0, 200); // time between 2 demo points
        public TimeSpan zapas = new TimeSpan(0, 0, 0, 0, 2000); // when you'll see next point. To support prediction functionality
        public Cursor cursor = new Cursor();
        public bool isGame = true;
        public List<SoundEffect> soundEffects = new List<SoundEffect>();
        public float lowVol = 0.25f;
        public int score = 0;
        public int scoreAdd = 100;
        public int maxScore = 4500;
        Texture2D background;
        Texture2D back_background;
        Texture2D readyTexture;
        public bool ready = false;
        public bool toPlay = true;
        public Ready readyO = null;
       public Dictionary<string,Texture2D> textures=new Dictionary<string,Texture2D>();
        public Vector2 musicSourcePosition = new Vector2(400, 240);
        public List<Ball> balls = new List<Ball>();

        




        VisualizationData visualizationData;
        float[] visualizationDataMas = new float[128];
        float[] visualizationDataMasPrev = new float[128];

        public Game1()
        {

            graphics = new GraphicsDeviceManager(this);

#if WINDOWS_PHONE
            graphics.PreferredBackBufferWidth = 800; // ширина приложения
            graphics.PreferredBackBufferHeight = 480; // высота приложения
            graphics.IsFullScreen = true; // флаг полноэкранного приложения

#else
            graphics.PreferredBackBufferWidth = 600; // ширина приложения
            graphics.PreferredBackBufferHeight = 750; // высота приложения
            graphics.IsFullScreen = false; // флаг полноэкранного приложения
#endif

            graphics.ApplyChanges(); // применяем параметры

            Content.RootDirectory = "Content";

            // base.OnExiting += new System.EventHandler(this.onExit);
        }



        /// <summary>
        /// Allows the game to perform any initialization it needs to before starting to run.
        /// This is where it can query for any required services and load any non-graphic
        /// related content.  Calling base.Initialize will enumerate through any components
        /// and initialize them as well.
        /// </summary>
        protected override void Initialize()
        {
            // TODO: Add your initialization logic here
            //IsFixedTimeStep = false;
            //graphics.SynchronizeWithVerticalRetrace = false;

            base.Initialize();

            
            

            readyO = new Ready(readyTexture, new Vector2(320, 240), 1);
#if !WINDOWS_PHONE
            demoFile = Directory.GetCurrentDirectory() + "\\" + song.Name + ".txt";
#else
            demoFile = song.Name + ".txt";
#endif
            for (int i = 0; i <3; i++)
            {
                MusicSrc a;
                // if (i<3)
                a = new MusicSrc(textures["player1"], new Vector2(180f , 95f + i * 100), new Vector2(), 0f, 0f, (int)(128 * i / MelList.Count), (int)(128 * (i + 1) / MelList.Count) - 1, 0.4f, 0.7f,this);
                //else
                //     a = new MusicSrc(MelList[i], new Vector2(100f + (i-3) * 70, 600f+i*10), new Vector2(), 0f, 0f, (int)(128 * i / MelList.Count), (int)(128 * (i + 1) / MelList.Count) - 1, 0.5f, 0.5f);

                musics.Add(a);

            }



            visualizationData = new VisualizationData();


            if (PRELOAD)
            {
                MediaPlayer.IsVisualizationEnabled = true;
            }
            else
            {
#if !WINDOWS_PHONE

                if (PRELOAD2)
                {
                    using (System.IO.FileStream fs = new System.IO.FileStream(demoFile, System.IO.FileMode.Open, System.IO.FileAccess.Read))
                    {
                        System.Runtime.Serialization.Formatters.Binary.BinaryFormatter b = new System.Runtime.Serialization.Formatters.Binary.BinaryFormatter();
                        DemoDatas = b.Deserialize(fs) as List<DemoData>;
                        fs.Close();
                    }
                    demoPoints = DemoDatas.Count();

                    foreach (DemoData a in DemoDatas)
                    {
                        for (int i = 0; i < 128; i++)
                        {
                            visualizationDataMasAvg[i] += a.timePayload[i] / demoPoints;
                        }


                    }
                }
                else
                {
                    string[] aa = File.ReadAllLines(demoFile + "x");
                    TimeSpan prevTime = new TimeSpan(0);
                    foreach (string a in aa)
                    {
                        string[] temp = a.Split(";".ToCharArray());
                        TimeSpan timesp = TimeSpan.Parse(temp[0]);
                        if (timesp - prevTime >= difficulty)
                        {
                            DemoDatas2.Add(new DemoData2(timesp, int.Parse(temp[1])));
                            prevTime = timesp;
                        }
                    }


                    demoPoints = DemoDatas2.Count();
                }
#else
                //string[] aa = File.ReadAllLines(demoFile + "x");
                Stream stream = TitleContainer.OpenStream("Content/" + demoFile + "x");
                using (StreamReader sr = new StreamReader(stream))
                {
                    TimeSpan prevTime = new TimeSpan(0);
                    string a;
                    while ((a = sr.ReadLine()) != null)
                    {
                        string[] temp = a.Split(";".ToCharArray());
                        TimeSpan timesp = TimeSpan.Parse(temp[0]);
                        if (timesp - prevTime >= difficulty)
                        {
                            DemoDatas2.Add(new DemoData2(timesp, int.Parse(temp[1])));
                            prevTime = timesp;
                        }
                    }
                }

                demoPoints = DemoDatas2.Count();
#endif


            }


        }

        /// <summary>
        /// LoadContent will be called once per game and is the place to load
        /// all of your content.
        /// </summary>
        protected override void LoadContent()
        {
            // Create a new SpriteBatch, which can be used to draw textures.
            spriteBatch = new SpriteBatchEx(GraphicsDevice);


            // TODO: use this.Content to load your game content here
            MelList = new List<Texture2D>();
            for (int a = 1; a <= 7; a++)
                MelList.Add(Content.Load<Texture2D>("a" + a.ToString()));

            background = Content.Load<Texture2D>("SA400178");
            back_background = Content.Load<Texture2D>("background");
            readyTexture = Content.Load<Texture2D>("ready");

            song = Content.Load<Song>(songFile);

            font = Content.Load<SpriteFont>("SpriteFont1");
            MouseIcon = Content.Load<Texture2D>("Mouse");


            soundEffects.Add(Content.Load<SoundEffect>("Miss2"));

            textures.Add("player1", Content.Load<Texture2D>("player1"));
            textures.Add("field", Content.Load<Texture2D>("field"));
            textures.Add("ball", Content.Load<Texture2D>("ball"));



        }

        /// <summary>
        /// UnloadContent will be called once per game and is the place to unload
        /// all content.
        /// </summary>
        protected override void UnloadContent()
        {
            // TODO: Unload any non ContentManager content here
        }

        /// <summary>
        /// Allows the game to run logic such as updating the world,
        /// checking for collisions, gathering input, and playing audio.
        /// </summary>
        /// <param name="gameTime">Provides a snapshot of timing values.</param>
        protected override void Update(GameTime gameTime)
        {
            if (ready && toPlay)
            {
                toPlay = false;

                MediaPlayer.Play(song);
                MediaPlayer.Volume = 1f;
                startTime = DateTime.Now;
                lastWriteTime = startTime;
                demoPointer = 0;
                score = 0;
                lastMaxTime = new TimeSpan(0);
            }
            // Allows the game to exit
            if (GamePad.GetState(PlayerIndex.One).Buttons.Back == ButtonState.Pressed)
                this.Exit();

            // TODO: Add your update logic here
            CursorStateUpdate();
            if (readyO != null)
                readyO.Update(this);

            if (ready)
            {

                int activeIndex = -1;

                if (PRELOAD)
                {
                    visualizationDataMas = new float[128];

                    MediaPlayer.GetVisualizationData(visualizationData);
                    for (int index = 0; index < 128; index++)
                    {
                        visualizationDataMas[index] = visualizationData.Frequencies[index];

                    }

                }



                timeSpa = new TimeSpan();
                timeSpa = DateTime.Now - startTime;

                if (DateTime.Now - lastWriteTime >= TimeBetweenWrites)
                {
                    lastWriteTime = DateTime.Now;

                    if (PRELOAD)
                    {

                        DemoDatas.Add(new DemoData(timeSpa, visualizationDataMas));


                    }
                    else
                    {
                        if (PRELOAD2)
                        {
                            if (timeSpa > DemoDatas[demoPointer].timeStamp)
                            {

                                if (demoPointer > 1)
                                    visualizationDataMasPrev = DemoDatas[demoPointer - 1].timePayload;

                                int diapazon = 25;
                                if (demoPointer > diapazon && demoPointer < demoPoints - diapazon - 1)
                                {
                                    visualizationDataMasAvg = new float[128];
                                    for (int k = -diapazon; k < diapazon; k++)
                                    {
                                        for (int i = 0; i < 128; i++)
                                        {
                                            visualizationDataMasAvg[i] += DemoDatas[demoPointer + k].timePayload[i] / (diapazon * 2);
                                        }
                                    }
                                }
                                visualizationDataMas = DemoDatas[demoPointer].timePayload;



                                demoPointer++;

                            }


                        }
                        else
                        {
                            if (demoPointer < demoPoints)
                            {
                                if (timeSpa > DemoDatas2[demoPointer].timeStamp)
                                {
                                    activeIndex = DemoDatas2[demoPointer].index;
                                    if (demoPointer < demoPoints - 1)
                                    {

                                        demoPointer++;
                                    }


                                }
                            }


                        }
                    }

                }

                // next points
                //if (demoPointer + 10 < demoPoints)
                {
                    var a = DemoDatas2.Where(x => x.timeStamp < timeSpa.Add(zapas) && x.timeStamp > lastMaxTime).ToArray();
                    if (a.Count() > 0)
                    {
                        lastMaxTime = a.Max(x => x.timeStamp);
                        foreach (DemoData2 b in a)
                        {
                            musics[b.index].nextPoints.Add(b.timeStamp);

                        }
                    }

                }

                // objects update
                if (!PRELOAD)
                {

                    if (PRELOAD2)
                    {
                        powers = new List<powerAddition>();
                        for (int index = 0; index < musics.Count; index++)
                        {
                            musics[index].Update(visualizationDataMas, visualizationDataMasAvg, visualizationDataMasPrev, this, index);
                        }

                        int mybeat = powers.OrderByDescending(x => x.power).ThenByDescending(y => y.addition).First().index;
                        if (musics[mybeat].power > 0)
                        {
                            musics[mybeat].Update2();
                            finalDemo.Add(timeSpa + ";" + mybeat);
                        }
                    }
                    else
                    {
                        if (activeIndex != -1)
                        {
                            if (!isGame)
                                musics[activeIndex].Update2();
                        }

                    }



                }



                for (int index = 0; index < musics.Count; index++)
                {
                    musics[index].Updater(this);
                }

                foreach (Ball ball in balls)
                {
                    ball.Update(this);
                }


            } //end of Ready

            base.Update(gameTime);
        }

        //cursor state
        public void CursorStateUpdate()
        {
            cursor.prevposition = cursor.position;
#if !WINDOWS_PHONE
            cursor.justPressed = false;
            cursor.position = new Vector2(Mouse.GetState().X, Mouse.GetState().Y);


            if (Mouse.GetState().LeftButton == ButtonState.Pressed)
            {
                if (cursor.pressed == false)
                    cursor.justPressed = true;
                else
                    cursor.justPressed = false;
                cursor.pressed = true;
            }
            else
                cursor.pressed = false;
#else
            TouchCollection touchState = TouchPanel.GetState();
            if (touchState.Count > 0)
            {
                TouchLocation touch = touchState.First();
                cursor.position = touch.Position;
                cursor.pressed = (touch.State == TouchLocationState.Pressed) || (touch.State == TouchLocationState.Moved);
                cursor.justPressed = (touch.State == TouchLocationState.Pressed);
            }
            else
            {
                cursor.pressed = false;
            }
#endif
            if (cursor.justPressed)
            { cursor.prevposition = cursor.position; }
            if (!cursor.pressed)
            {
                cursor.draggedObject = null;
            }


        }

        /// <summary>
        /// This is called when the game should draw itself.
        /// </summary>
        /// <param name="gameTime">Provides a snapshot of timing values.</param>
        protected override void Draw(GameTime gameTime)
        {

            GraphicsDevice.Clear(Color.CornflowerBlue);

            // TODO: Add your drawing code here
            spriteBatch.Begin(SpriteSortMode.Immediate,BlendState.NonPremultiplied);

            spriteBatch.Draw(back_background, new Vector2(0, 0), null, new Color(1, 1, 1, 0.7f), 0f, new Vector2(0, 0), 1, SpriteEffects.None, 1f);
            spriteBatch.Draw(textures["field"], new Vector2(0, 0), null, new Color(1, 1, 1, 0.7f), 0f, new Vector2(0, 0), 1, SpriteEffects.None, 1f);

            foreach (Ball ball in balls)
            {
                ball.Draw(spriteBatch);
            }

            if (ready)
            {
                for (int index = 0; index < musics.Count; index++)
                {
                    musics[index].Draw2(spriteBatch, timeSpa, zapas, this);

                }

                /////////////////////////draw image according to score
                //if (score > 0) 
                //{
                //    int width = 1;
                //    int height = 1;

                //    if ((score < maxScore))
                //    {
                //        float coef = ((float)score / maxScore);
                //        width = (int)Math.Floor(coef * background.Width);
                //        height = (int)Math.Floor(coef * background.Height);
                //    }
                //    else
                //    {
                //        width = background.Width;
                //        height = background.Height;

                //    }
                //    Vector2 origin1 = new Vector2(background.Width / 2, background.Height / 2);
                //    spriteBatch.Draw(background, new Vector2(610 - width / 2, 500 - height / 2), new Rectangle((background.Width - width) / 2, (background.Height - height) / 2, width, height), new Color(1, 1, 1, 0.7f), 0f, origin1, 0.95f, SpriteEffects.None, 1f);
                //}
                /////////////////////////// End of draw image according to score
                //Font

                //for (int index = 0; index < 128; index++)
                //{
                //    string suffix = "";
                //    if (visualizationDataMas[index] > 0.6)
                //        suffix = "        !!!!!!!!!!!";
                //    string output = index.ToString() + ": " + visualizationDataMas[index] + suffix;

                //    // Find the center of the string
                //    Vector2 FontOrigin = font.MeasureString(output) / 2;
                //    // Draw the string
                //    spriteBatch.DrawString(font, output, new Vector2(4f, 10f + index * 8), Color.LightGreen);
                //    //Note: Change "CourierNew" to "current" above to enable switching


                //}

                string output = "Score: " + score;

                // Find the center of the string
                Vector2 FontOrigin = font.MeasureString(output) / 2;
                // Draw the string
                spriteBatch.DrawString(font, output, new Vector2(16f, 16f), Color.LightGreen);
                // end of Font

                //objects
                for (int index = 0; index < musics.Count; index++)
                {
                    musics[index].Draw(spriteBatch, timeSpa, zapas, this);

                }


            }
            Vector2 origin = new Vector2(MouseIcon.Width / 2, MouseIcon.Height / 2);
            spriteBatch.Draw(MouseIcon, cursor.position, new Rectangle(0, 0, MouseIcon.Width, MouseIcon.Height), Color.MintCream, 0f, origin, 0.1f, SpriteEffects.None, 1f);
             
            if (readyO != null)
                readyO.Draw(spriteBatch, this);

           // spriteBatch.Drawl
           // spriteBatch.DrawLine(new Vector2(100, 100), cursor.position, Color.Black);
            //spriteBatch.DrawRectangle(new Vector2(100, 100), cursor.position, Color.Black);

            spriteBatch.End();

            base.Draw(gameTime);
        }



        protected override void OnExiting(Object sender, EventArgs args)
        {
            base.OnExiting(sender, args);
#if !WINDOWS_PHONE

            if (PRELOAD)
            {

                using (System.IO.FileStream fs = new System.IO.FileStream(demoFile, System.IO.FileMode.OpenOrCreate, System.IO.FileAccess.Write))
                {
                    System.Runtime.Serialization.Formatters.Binary.BinaryFormatter b = new System.Runtime.Serialization.Formatters.Binary.BinaryFormatter();
                    b.Serialize(fs, DemoDatas);
                    fs.Close();
                }


            }

            if (PRELOAD2)
            {
                File.WriteAllLines(demoFile + "x", finalDemo, System.Text.Encoding.ASCII);
            }
#else

#endif
            // Stop the threads
        }

    }
}
