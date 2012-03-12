
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
    public class Ready
    {
        public Texture2D Texture { get; set; }        // Текстура частицы
        public Vector2 Position { get; set; }        // Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
       
        public float Size { get; set; }                // Размер частицы

        public Ready(Texture2D texture, Vector2 position, float size)
        {
            // Установка переменных из конструктора
            Texture = texture;
            Position = position;
           

            Size = size;
            
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
        private bool isNavigated(Game1 game)
        {
            bool result = false;
            
                if (game.cursor.position.X > (Position.X - Texture.Width * Size / 2) && game.cursor.position.X < (Position.X + Texture.Width * Size / 2) && game.cursor.position.Y > (Position.Y - Texture.Height / 2 * Size) && game.cursor.position.Y < (Position.Y + Texture.Height / 2 * Size))
                {
                    result = true;

                }
            
            return result;
        }

        public void Update(Game1 game)
        {
            if (isPressed(game))
            {
                //game.readyO = null;
                Position = new Vector2(470, 16);
                Size = 0.7f;

                //game.score = 0;
                game.demoPointer = 0;

                game.ready = true;
                game.toPlay = true;
            }
            if (game.demoPointer >= game.demoPoints - 1)
            {
                Position = new Vector2(350, 350);
                Size = 1f;

            }
        }

        public void Draw(SpriteBatch spriteBatch, Game1 game) // Прорисовка частички
        {

            float mnoz = 0.8f;
            if (isNavigated(game))
                mnoz = 1f;

            Rectangle sourceRectangle = new Rectangle(0, 0, Texture.Width, Texture.Height);
            Vector2 origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            spriteBatch.Draw(Texture, Position, sourceRectangle, new Color(1, 1, 1, 1f),
              0, origin, Size*mnoz , SpriteEffects.None, 0f);

        }
    }
}
