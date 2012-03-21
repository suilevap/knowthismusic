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
    public class Ball
    {

         public Texture2D Texture { get; set; }        // Текстура частицы
        public Vector2 Position { get; set; }
        public Vector2 TargetPosition { get; set; }// Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
        public Vector4 color { get; set; }            // Цвет частицы
        public float Size { get; set; }                // Размер частицы

        public float alpha = 1f;
           private Vector2 origin;


           public int score = 0;
         int maxScore = 10;
         float friction = 0.9f;
         float strength = 0.05f;
        
       
         Random random=new Random(); // Генератор случайных чисел

        public Ball(Texture2D texture, Vector2 position, Vector2 velocity,
            float angle, float angularVelocity, float size)
        {
            // Установка переменных из конструктора
            Texture = texture;
            Position = position;
            TargetPosition = position;
            Velocity = velocity;
            Angle = angle;
            AngularVelocity = angularVelocity;
            Size = size;
            
            color = new Vector4(1f, 1f, 1f, alpha);
            origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            
        }

        public void Update(Game1 game)
        {

            if (isDragged(game))
            {
                Velocity = new Vector2(0);
                Position += game.cursor.position - game.cursor.prevposition;
            }
            else
            {
                if (score > maxScore)
                    score = maxScore;
                strength = 0.06f+(1-(float)score/maxScore)*0.2f;                
                if (Velocity.Length() < (TargetPosition - Position).Length() * strength)
                    Velocity = (TargetPosition - Position) * strength;
                Position += Velocity;
                Angle += AngularVelocity;
                Velocity = Velocity * friction;
            }


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
            return result;
        }

        public void Draw(SpriteBatchEx spriteBatch) // Прорисовка частички
        {

            spriteBatch.Draw(Texture, Position, null, new Color(color),
               Angle, origin, Size*((float)score/maxScore), SpriteEffects.None, 0f);
        }
    }
}
