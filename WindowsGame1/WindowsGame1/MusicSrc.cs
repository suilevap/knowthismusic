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
   public class MusicSrc
    {
        Texture2D Texture { get; set; }        // Текстура частицы
        public Vector2 Position;        // Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
        Vector4 color;
        Vector4 mergeColor;
        float Size { get; set; }                // Размер частицы
        float orbitRange = 70;
        float orbitAngle = 0;
        int orbitDirection = 1;
        bool constructed = false;


        float alpha = 1f;


        private int MinFreq;
        private int MaxFreq;
        private float React;// Тип частицы// Тип частицы
        public int power;
        //int score = 0;
        //int maxScore = 10;
       
        public List<TimeSpan> nextPoints = new List<TimeSpan>();
        Random random = new Random(); // Генератор случайных чисел
        public List<Ball> myballs=new List<Ball>();
        Game1 gameobj;
        bool isStatic = true;

        public MusicSrc(Texture2D texture, Vector2 position, Vector2 velocity,
            float angle, float angularVelocity, int minFreq, int maxFreq, float react, float size, Game1 game, Vector4 colorr)
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
            gameobj = game;

            color = colorr;
            orbitAngle = (float)(random.NextDouble() * Math.PI * 2);
            if (random.NextDouble() >= 0.5)
                orbitDirection = -1;
            NewBallCreate();
            



        }

        public void NewBallCreate()
        {
            if (color.X > 0)
            {
                Ball myball = new Ball(gameobj.textures["player1"], Position, new Vector2(0), 0, 0, 0.5f, new Vector4(1, 0, 0, 1), this, (color.X));
                myballs.Add(myball);

                gameobj.balls.Add(myball);
            }
            if (color.Y > 0)
            {
                Ball myball = new Ball(gameobj.textures["player1"], Position, new Vector2(0), 0, 0, 0.5f, new Vector4(0, 1, 0, 1), this, (color.Y ));
                myballs.Add(myball);

                gameobj.balls.Add(myball);
            }
            if (color.Z > 0)
            {
                Ball myball = new Ball(gameobj.textures["player1"], Position, new Vector2(0), 0, 0, 0.5f, new Vector4(0, 0, 1, 1), this, (color.Z));
                myballs.Add(myball);

                gameobj.balls.Add(myball);
            }
            myballs = myballs.OrderBy(x => x.score).ToList();
        }

        public void Update(float[] visualizationData, float[] visualizationDataAvg, float[] visualizationDataPrev, Game1 game, int index) // Обновление единичной частички
        {
                                                          



        }

        public void MergeColorUpdate()
        {
            mergeColor = new Vector4(0, 0, 0, 1);

            
            foreach (Ball myball in myballs)
            {
                if (myball.color != new Vector4(1, 1, 1, 1))
                {
                    mergeColor += myball.color * (float)myball.score / myball.maxScore;
                    mergeColor.W = 1;
                }
            }
 
        }

        public void Updater(Game1 game)
        {
            if ((mergeColor - color).Length() == 0 )
                constructed = true;
            else
                constructed = false;

            float angadd = 0;
            foreach (Ball myball in myballs)
            {
                
                orbitAngle += orbitDirection * (0.001f * (1.2f - myball.Size2));

                myball.TargetPosition.X = Position.X + orbitRange * (1 ) * (float)Math.Cos(orbitAngle + angadd);
                myball.TargetPosition.Y = Position.Y + orbitRange * (1 ) * (float)Math.Sin(orbitAngle + angadd);
                angadd += (float)(Math.PI / 4);
            }

            if (isDragged(game))
            {
                Position += game.cursor.position - game.cursor.prevposition;
                foreach (Ball myball in myballs)
                {
                    myball.TargetPosition += game.cursor.position - game.cursor.prevposition;
                }
            }

            if (Angle != 0)
            {
                float k = 0.2f;
                float f = Math.Abs(k * Angle);
                if (Angle > 0)
                    Angle -= (float)Math.Sqrt(f * 2) / 10;
                else
                    Angle += (float)Math.Sqrt(f * 2) / 10;



            }

            
            if (game.isGame)
            {
                if (isPressed(game))
                {
                   // bool missClick = false;
                    alpha = 1;

                                                            

                   


                }

            }
            color.W=alpha;
            
        }

        private bool isPressed(Game1 game)
        {
            bool result = false;
            if (game.cursor.justPressed)
            {
                if (game.cursor.position.X > (Position.X - Texture.Width * Size / 2) && game.cursor.position.X < (Position.X + Texture.Width * Size / 2) && game.cursor.position.Y > (Position.Y - Texture.Height / 2 * Size) && game.cursor.position.Y < (Position.Y + Texture.Height / 2 * Size))
                {
                    result = true;

                }
            }
            return result;
        }
        private bool isDragged(Game1 game)
        {
            bool result = false;
            if (!isStatic)
            {
                if (game.cursor.pressed)
                {
                    if (game.cursor.prevposition.X > (Position.X - Texture.Width * Size / 2) && game.cursor.prevposition.X < (Position.X + Texture.Width * Size / 2) && game.cursor.prevposition.Y > (Position.Y - Texture.Height / 2 * Size) && game.cursor.prevposition.Y < (Position.Y + Texture.Height / 2 * Size))
                    {
                        if (game.cursor.draggedObject == null || game.cursor.draggedObject == this)
                        {
                            game.cursor.draggedObject = this;
                            result = true;
                        }

                    }
                }
            }
            return result;
        }

        public void Update2() // Обновление единичной частички2
        {

            alpha = 1;


        }



        public void Draw(SpriteBatchEx spriteBatch, TimeSpan timeSpa, TimeSpan zapas, Game1 game) // Прорисовка частички
        {

            Vector2 origin = new Vector2(Texture.Width / 2, Texture.Height / 2);


            


            spriteBatch.Draw(Texture, Position, null, new Color(color),
                Angle, origin, Size, SpriteEffects.None, 0f);
            spriteBatch.Draw(Texture, Position, null, new Color(mergeColor),
                Angle, origin, Size*0.4f, SpriteEffects.None, 0f);
            if (constructed)
            {
                origin = new Vector2(game.textures["rock"].Width / 2, game.textures["rock"].Height / 2);
                spriteBatch.Draw(game.textures["rock"], Position, null, Color.White, Angle, origin, Size * 0.1f, SpriteEffects.None, 0f);
            }




        }

        public void Draw2(SpriteBatch spriteBatch, TimeSpan timeSpa, TimeSpan zapas, Game1 game) // Прорисовка частички
        {

            //Vector2 origin = new Vector2(Texture.Width / 2, Texture.Height / 2);

            //Vector4 colo = color;
            //colo.W = 0.9f;
            //spriteBatch.Draw(Texture, Position, null, new Color(colo),
            //  0, origin, Size * 0.85f, SpriteEffects.None, 0f);


        }


    }
}
