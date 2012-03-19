using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Audio;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.GamerServices;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using Microsoft.Xna.Framework.Media;

namespace WindowsGame1
{
    class Ball
    {

         public Texture2D Texture { get; set; }        // Текстура частицы
        public Vector2 Position { get; set; }        // Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
        public Vector4 color { get; set; }            // Цвет частицы
        public float Size { get; set; }                // Размер частицы

        public float alpha = 1f;
           private Vector2 origin;


           public int score = 0;
         int maxScore = 10;
        
       
         Random random=new Random(); // Генератор случайных чисел

        public Ball(Texture2D texture, Vector2 position, Vector2 velocity,
            float angle, float angularVelocity, float size)
        {
            // Установка переменных из конструктора
            Texture = texture;
            Position = position;
            Velocity = velocity;
            Angle = angle;
            AngularVelocity = angularVelocity;
            Size = size;
            
            color = new Vector4(1f, 1f, 1f, alpha);
            origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            
        }

        public void Update()
        {
            Position += Velocity;
            Angle += AngularVelocity;
        }

        public void Draw(SpriteBatchEx spriteBatch) // Прорисовка частички
        {

            spriteBatch.Draw(Texture, Position, null, new Color(color),
               Angle, origin, Size*((float)score/maxScore), SpriteEffects.None, 0f);
        }
    }
}
