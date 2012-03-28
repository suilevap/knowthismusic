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
        public Vector2 TargetPosition; // Позиция частицы
        public Vector2 Velocity { get; set; }        // Скорость частицы
        public float Angle { get; set; }            // Угол поворота частицы
        public float AngularVelocity { get; set; }    // Угловая скорость частицы
        public Vector4 color;            // Цвет частицы
        public float Size { get; set; }
        public float Size2 = 1;// Размер частицы
        public float Size2realtime = 0;
        float sizeVelocity = 0;
        public float alpha = 1f;
        private Vector2 origin;
        public float range;
        public MusicSrc parentMusicSrc;


        public int score = 0;
        int maxScore = 20;
        float friction = 0.9f;
        float strength = 0.05f;
        //List<Ball> collisions = new List<Ball>();


        Random random = new Random(); // Генератор случайных чисел

        public Ball(Texture2D texture, Vector2 position, Vector2 velocity,
            float angle, float angularVelocity, float size, Vector4 colorr, MusicSrc parentSource)
        {
            // Установка переменных из конструктора
            Texture = texture;
            Position = position;
            TargetPosition = position;
            Velocity = velocity;
            Angle = angle;
            AngularVelocity = angularVelocity;
            Size = size;
            parentMusicSrc = parentSource;
            color = colorr;
            color.W = alpha;
            origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            range = Texture.Width / 2 * Size * Size2realtime;

        }
        public void Collisions(Game1 game)
        {
            //collisions = new List<Ball>();
            Ball toRemove = null;
            Ball collides = null;
            foreach (Ball a in game.balls)
            {
                if (a != this)
                {
                    float distance = (a.Position - this.Position).Length();
                    if (distance < a.range + this.range && a.score>0 && this.score>0)
                    {
                        //collisions.Add(a);
                        collides = a;
                        if (this.score < a.score)
                            toRemove = this;
                        else if (this.score > a.score)
                            toRemove = a;
                        else
                        {
                            if (this.Velocity.Length() > a.Velocity.Length())
                                toRemove = this;
                            else
                                toRemove = a;
                        }
                        break;
                       

                    }
                }
            }
            if (toRemove != null)
            {
                game.ballToRemove = toRemove;

                Vector4 resultColor = collides.color * (float)collides.score / (collides.score + this.score) + this.color * (float)this.score / (collides.score + this.score);
                int resultScore = (int)Math.Floor((collides.score + this.score)*1.2f);
                //resultColor.Normalize();
                if (toRemove == this)
                {
                    collides.color = resultColor;
                    collides.score = resultScore;
                    
                }
                if (toRemove == collides)
                {
                    this.color = resultColor;
                    this.score = resultScore;
                    
                }
            }
        }

        public void Update(Game1 game)
        {

            if (score > maxScore)
                score = maxScore;
            Size2 = (float)Math.Sin((float)score / maxScore * (float)Math.PI / 2) * 0.8f + 0.2f;
            if (isDragged(game))
            {
                Vector2 dPos = game.cursor.position - game.cursor.prevposition;
                Velocity = (Velocity + dPos) / 2;
                Position += dPos;
            }
            else
            {

                strength = 0.01f + (1 - Size2) * 0.02f;
                Velocity += (TargetPosition - Position) * strength;
                Position += Velocity;
                Angle += AngularVelocity;

            }
            Velocity = Velocity * friction;

            if (Size2realtime != Size2)
            {
                sizeVelocity += (Size2 - Size2realtime) * strength;
                Size2realtime += sizeVelocity;
                sizeVelocity = sizeVelocity * friction;


            }
            range = Texture.Width / 2 * Size * Size2realtime;
            Collisions(game);

        }

        private bool isPressed(Game1 game)
        {
            bool result = false;
            if (game.cursor.justPressed)
            {
                if (game.cursor.position.X > (Position.X - Texture.Width * Size * Size2 / 2) && game.cursor.position.X < (Position.X + Texture.Width * Size * Size2 / 2) && game.cursor.position.Y > (Position.Y - Texture.Height / 2 * Size * Size2) && game.cursor.position.Y < (Position.Y + Texture.Height / 2 * Size * Size2))
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
                if (game.cursor.prevposition.X > (Position.X - Texture.Width * Size * Size2 / 2) && game.cursor.prevposition.X < (Position.X + Texture.Width * Size * Size2 / 2) && game.cursor.prevposition.Y > (Position.Y - Texture.Height / 2 * Size * Size2) && game.cursor.prevposition.Y < (Position.Y + Texture.Height / 2 * Size * Size2))
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
            spriteBatch.DrawLine(Position, TargetPosition, Color.Black, 1);
            spriteBatch.Draw(Texture, TargetPosition, null, new Color(color), Angle, origin, 0.08f, SpriteEffects.None, 0f);
            spriteBatch.Draw(Texture, Position, null, new Color(color), Angle, origin, Size * Size2realtime, SpriteEffects.None, 0f);
        }
    }
}
