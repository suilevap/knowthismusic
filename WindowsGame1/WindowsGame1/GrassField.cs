using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    class GrassField:IDrawableUpdatable
    {

        private List<Grass> data;
        private Rectangle _rect;
        public Game1 Game;
        public int Depth { get; set; } 

        public GrassField(Rectangle rect, int n)
        {
            data = new List<Grass>();
            Random rnd = new Random();
            for (int i = 0; i < n; i++)
            {
                Vector2 pos = new Vector2(rnd.Next(rect.Left, rect.Right), rnd.Next(rect.Top, rect.Bottom));
                //float l = rnd.Next(rect.Height/8, rect.Height/2);
                float l = (float)((pos.Y - rect.Top) * (0.75 + 0.5 * rnd.NextDouble()) + 8);
                float k1 = (float) (2.5 + 1.5*rnd.NextDouble());
                float k2 = (float) (k1 + 1 - 2*rnd.NextDouble());
                Color color = Color.Lerp(Color.Green, Color.Yellow, (float)(0.5*rnd.NextDouble()));
                Grass grass = new Grass(pos, new Vector2(l/2, l/2), new Vector2(k1, k2), color, 0.1f);
                grass.AddSpeed(new Vector2((float)(rnd.NextDouble()*Math.PI/2), (float)(rnd.NextDouble()*Math.PI/2)));
                data.Add(grass);
            }
            _rect = rect;
            data = data.OrderBy(x => x.Position.Y).ToList();
        }

        public void Update(Game1 game, GameTime time)
        {
            
        }

        public void Draw(SpriteBatchEx spriteBatch, GameTime time)
        {
            spriteBatch.DrawRectangle(new Vector2(_rect.Left, _rect.Top + 1), new Vector2(_rect.Right, _rect.Bottom), Color.Green);

            float sp = 1f+(Game.cursor.speed.X);
            Vector2 speed = new Vector2(sp, sp / 2);
            speed = speed * time.ElapsedGameTime.Milliseconds / 1000.0f * (float)Math.PI / 4;

            foreach (var grass in data)
            {
                //if (sp != 0)
                //{
                //    if ((grass.Position - Game.cursor.position).LengthSquared() < 256 * 256)
                //    {
                //        grass.AddSpeed(speed * (1 - Math.Abs(grass.Position.X - Game.cursor.position.X) / 256));
                //    }
                //}
                grass.Draw(spriteBatch, time);
            }
        }
    }
}
