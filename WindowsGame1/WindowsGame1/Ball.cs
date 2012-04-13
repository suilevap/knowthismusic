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
        public Vector4 targetColor;
        public Vector4 color;// Цвет частицы
        public float Size { get; set; }
        public float Size2 = 1;// Размер частицы
        public float Size2realtime = 0;
        float sizeVelocity = 0;
        public float alpha = 1f;
        private Vector2 origin;
        public float range;
        public MusicSrc parentMusicSrc;
        public bool collidable = false;


        public float score = 0;
        public float maxScore = 1;
        float friction = 0.9f;
        float strength = 0.05f;
        float nStrength = 50;
        Elastic positionElastic;
        Texture2D textureCircle;
        Texture2D textureCircleInactive;
        
        //List<Ball> collisions = new List<Ball>();


        Random random = new Random(); // Генератор случайных чисел

        public Ball(Texture2D texture, Vector2 position, Vector2 velocity,
            float angle, float angularVelocity, float size, Vector4 colorr, MusicSrc parentSource,float Score, Game1 game)
        {
            
            Texture = texture;
            textureCircle = game.textures["player1circle"];
            textureCircleInactive = game.textures["player1inactive"];
            Position = position;
            TargetPosition = position;
            Velocity = velocity;
            Angle = angle;
            AngularVelocity = angularVelocity;
            Size = size;
            
            parentMusicSrc = parentSource;
            targetColor = colorr;
            color = new Vector4(0);
            color.W = alpha;
            score = Score;
            origin = new Vector2(Texture.Width / 2, Texture.Height / 2);
            range = Texture.Width / 2 * Size * Size2realtime;

            positionElastic = new Elastic()
           {
               Origin = TargetPosition,
               Friction = 5f,
               Position = position,
               Speed = new Vector2(),
               K = new Vector2(nStrength, nStrength)
           }; 

        }
        public void Collisions(Game1 game)
        {
            
            if (!collidable)
            {
            Ball collides = null;
            foreach (Ball a in game.balls)
            {
                if (a != this)
                {
                    float distance = (a.Position - this.Position).Length();
                    if (distance < a.range + this.range && a.collidable && a.score>0 && this.score>0)
                    {
                        
                        collides = a;
                        {
                            this.color = collides.color;
                            if (parentMusicSrc != null)
                                parentMusicSrc.MergeColorUpdate();
                            

                        }
                        
                        break;
                       

                    }
                }
            }
        }
            
        }

        public void Update(Game1 game, GameTime gameTime)
        {
            
            if (score > maxScore)
                score = maxScore;
            Size2 = (float)Math.Sqrt((float)score / maxScore) * 1f;// + 0.1f;
            //Size2 = ((float)score / maxScore) * 1f + 0;
            if (isDragged(game))
            {
                Vector2 dPos = game.cursor.position - game.cursor.prevposition;
               // Velocity = (Velocity + dPos) / 2;
                //Position += dPos;
                
                positionElastic.Position += dPos;
                positionElastic.Speed = (positionElastic.Speed + dPos * 50) / 2;
                
            }
            else
            {
                positionElastic.K = new Vector2(nStrength + (1 - Size2) * nStrength / 5, 50f + (1 - Size2) * nStrength/5);
                positionElastic.Origin = TargetPosition;
                positionElastic.Update(gameTime);
                
                //strength = 0.01f + (1 - Size2) * 0.02f;
                
                //Velocity += (TargetPosition - Position) * strength;
                //Position += Velocity;
                Angle += AngularVelocity;

            }
            //Velocity = Velocity * friction;

            Position = positionElastic.Position;

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
                if (game.cursor.prevposition.X > (Position.X - Texture.Width * Size  / 2) && game.cursor.prevposition.X < (Position.X + Texture.Width * Size   / 2) && game.cursor.prevposition.Y > (Position.Y - Texture.Height / 2 * Size ) && game.cursor.prevposition.Y < (Position.Y + Texture.Height / 2 * Size ))
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

        public void Draw(SpriteBatchEx spriteBatch, Game1 game) // Прорисовка частички
        {
            if (parentMusicSrc != null)
                spriteBatch.DrawLine(parentMusicSrc.Position, TargetPosition , Color.Black, 1);
            
            if ((Position-TargetPosition).Length()>16)
            {
            float alph = ((Position - TargetPosition).Length()-16) / 96;
            
            spriteBatch.DrawLine(Position, TargetPosition, new Color(0,0,0,alph), 1);
            spriteBatch.Draw(Texture, TargetPosition, null, new Color(0, 0, 0, alph), Angle, origin, 0.08f, SpriteEffects.None, 0f);
        }
          //  else
            spriteBatch.Draw(textureCircle, Position, null, Color.White, Angle, origin, Size, SpriteEffects.None, 0f);
            
            if (color==new Vector4(0,0,0,1))
                spriteBatch.Draw(textureCircleInactive, Position, null, Color.White, Angle, origin, Size * Size2realtime, SpriteEffects.None, 0f);
            else
            spriteBatch.Draw(Texture, Position, null, new Color(color), Angle, origin, Size * Size2realtime, SpriteEffects.None, 0f);

            if (!collidable)
            {
                
                string output = string.Format("{0}", (int)(score * 255));
                //Find the center of the string
                Vector2 FontOrigin = game.font.MeasureString(output) / 2;
                //Draw the string
                spriteBatch.DrawString(game.font, output, Position, Color.Black, 0, FontOrigin, 1, SpriteEffects.None, 0);
            }
           
            
        }
    }
}
