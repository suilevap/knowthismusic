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


namespace WindowsGame1
{
    class MusicSrc
    {
        public Texture2D Texture { get; set; }        // Текстура частицы
        public Vector2 Position { get; set; }        // Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
        public Vector4 color { get; set; }            // Цвет частицы
        public float Size { get; set; }                // Размер частицы

        public float alpha = 1f;

        private float RComponent; // Красный компонент RGB
        private float GComponent; // Зеленый компонент RGB
        private float BComponent; // Синий компонент RGB
        private int MinFreq;
        private int MaxFreq;
        private float React;// Тип частицы// Тип частицы
        public int power;
        private float sumAdd;
        public List<TimeSpan> nextPoints = new List<TimeSpan>();
         Random random=new Random(); // Генератор случайных чисел

        public MusicSrc(Texture2D texture, Vector2 position, Vector2 velocity,
            float angle, float angularVelocity, int minFreq, int maxFreq, float react, float size)
        {
            // Установка переменных из конструктора
            Texture = texture;
            Position = position;
            Velocity = velocity;
            Angle = angle;
            AngularVelocity = angularVelocity;

            Size = size;
            MinFreq = minFreq;
            MaxFreq = maxFreq;
            React = react;

            Color StartColor = new Color(1f, 0f, 0f); // Обычная



            RComponent = ((int)StartColor.R) / 255f;
            GComponent = ((int)StartColor.G) / 255f;
            BComponent = ((int)StartColor.B) / 255f;

            color = new Vector4(1f, 1f, 1f, alpha);



        }

        public void Update(float[] visualizationData, float[] visualizationDataAvg, float[] visualizationDataPrev, Game1 game,int index) // Обновление единичной частички
        {
            
            power = 0;
            sumAdd = 0;
            for (int i = MinFreq; i < MaxFreq; i++)
            {

                float addition = 0;
                if (visualizationDataAvg[i]>0.41)
                addition=(float)(visualizationData[i] - visualizationDataPrev[i] * 1.06);
                else
                    addition = (float)(visualizationData[i] - visualizationDataPrev[i] * 1.4);

                if (visualizationData[i] > visualizationDataAvg[i] * 1.09 && addition>0)
                {
                    power++;
                    sumAdd += addition;
                }
            }
            //if (power > 0)
            {
                game.powers.Add(new powerAddition(power, sumAdd,index));
                
                
            }
            //if (power != 0)
            //{
            //    if (alpha < power / (MaxFreq - MinFreq))//power / (MaxFreq - MinFreq))
            //    {
            //        alpha += power / (MaxFreq - MinFreq);
            //        if (alpha > 1)
            //            alpha = 1;
            //    }
            //}
            //if (alpha < 0.2f &&  power / (MaxFreq - MinFreq)>0.2f)//power / (MaxFreq - MinFreq))
            //  alpha = power/ (MaxFreq - MinFreq);

            

        }

        public void Updater(Game1 game)
        {
            if (isPermPressed(game))
            {
                Position += game.cursor.position - game.cursor.prevposition;
            }

            if (Angle!=0)
            {
                float k=0.2f;
                float f = Math.Abs(k * Angle);
                if (Angle>0)
                Angle -= (float)Math.Sqrt(f  * 2)/5;
                else
                    Angle += (float)Math.Sqrt(f  * 2)/5;



            }

            if (nextPoints.Count() != 0)
            {
                List<TimeSpan> toRemove = new List<TimeSpan>();
                foreach (TimeSpan ts in nextPoints)
                {
                    if (game.timeSpa >= ts+game.pogreshn)
                    {
                        toRemove.Add(ts);
                                                
                    }
                }
                if (toRemove.Count() > 0)
                {
                    MediaPlayer.Volume = game.lowVol;
                    
                    foreach (TimeSpan ts in toRemove)
                    {
                        nextPoints.Remove(ts);

                    }

                }
            }
            if (game.isGame)
            {
                if (isPressed(game))
                {
                    bool missClick=false;
                    alpha = 1;

                    
                    if (nextPoints.Count() != 0)
                    {
                        if (game.timeSpa - nextPoints[0] < game.pogreshn && game.timeSpa - nextPoints[0] > -game.pogreshn)
                        {
                            MediaPlayer.Volume = 1;
                            game.score += (int)Math.Floor((float)(game.scoreAdd * (1 - Math.Abs(((float)(game.timeSpa - nextPoints[0]).Ticks) / game.pogreshn.Ticks))));
                            nextPoints.RemoveAt(0);
                            Angle = -((float)random.Next(100)/100)+0.5f;
                           
                        }
                        else
                            missClick = true;

                    }
                    else
                        missClick = true;

                    if (missClick)
                    {
                        MediaPlayer.Volume = game.lowVol;
                        
                        game.soundEffects[0].Play();
                        game.score -= game.scoreAdd/2;
                        
                    }
                    

                }
                 
            }
            color = new Vector4(1f, 1f, 1f, alpha);
            if (alpha > 0)
            {
                alpha -= 0.03f;


            }
        }

        private bool isPressed(Game1 game)
        {
            bool result = false;
            if (game.cursor.justPressed)
            {
                if (game.cursor.position.X > (Position.X - Texture.Width * Size / 2) && game.cursor.position.X < (Position.X + Texture.Width*Size / 2 ) && game.cursor.position.Y > (Position.Y - Texture.Height / 2 * Size) && game.cursor.position.Y < (Position.Y + Texture.Height / 2 * Size))
                {
                    result = true;
                    
                }
            }
            return result;
        }
        private bool isPermPressed(Game1 game)
        {
            bool result = false;
            if (game.cursor.pressed)
            {
                if (game.cursor.prevposition.X > (Position.X - Texture.Width * Size / 2) && game.cursor.prevposition.X < (Position.X + Texture.Width * Size / 2) && game.cursor.prevposition.Y > (Position.Y - Texture.Height / 2 * Size) && game.cursor.prevposition.Y < (Position.Y + Texture.Height / 2 * Size))
                {
                    result = true;

                }
            }
            return result;
        }

        public void Update2() // Обновление единичной частички2
        {
            
            alpha = 1;
       

        }

        

        public void Draw(SpriteBatch spriteBatch,TimeSpan timeSpa, TimeSpan zapas, Game1 game) // Прорисовка частички
        {
            Rectangle sourceRectangle = new Rectangle(0, 0, Texture.Width, Texture.Height);
            Vector2 origin = new Vector2(Texture.Width / 2, Texture.Height / 2);

            
            if (nextPoints.Count() > 0)
            {
                List<TimeSpan> toRemove = new List<TimeSpan>();
                foreach (TimeSpan ts in nextPoints)
                {
                  
                    {
                        Single coef;
                        Vector2 po;
                        //if (ts >= timeSpa)
                        {
                            coef = ((float)((ts - timeSpa).Ticks) / zapas.Ticks);
                            po = new Vector2(Position.X, Position.Y - (float)Math.Sin(coef * 3.1416 / 2) * 500);
                        }
                        
                        float al=0.4f*(1-coef);
                        if (coef < 0)
                            al = 0.4f * (1 - Math.Abs(coef)*10);
                        Vector4 colo = new Vector4(1, 1, 1, al);
                        spriteBatch.Draw(Texture, po, sourceRectangle, new Color(colo),
                0, origin, Size*(1-Math.Abs(coef)), SpriteEffects.None, 0f);
 
                    }
                }
                
            }

           
            spriteBatch.Draw(Texture, Position, sourceRectangle, new Color(color),
                Angle, origin, Size, SpriteEffects.None, 0f);


        }

        public void Draw2(SpriteBatch spriteBatch, TimeSpan timeSpa, TimeSpan zapas, Game1 game) // Прорисовка частички
        {
            Rectangle sourceRectangle = new Rectangle(0, 0, Texture.Width, Texture.Height);
            Vector2 origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            spriteBatch.Draw(Texture, Position, sourceRectangle, new Color (1,1,1,0.3f),
              0, origin, Size*0.85f, SpriteEffects.None, 0f);


        }


    }
}
