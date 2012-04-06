using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    class GrassField
    {

        private List<Grass> data;

        public GrassField(Rectangle rect, int n)
        {
            data = new List<Grass>();
            Random rnd = new Random();
            for (int i = 0; i < n; i++)
            {
                Vector2 pos = new Vector2(rnd.Next(rect.Left, rect.Right), rnd.Next(rect.Top, rect.Bottom));
                float l = rnd.Next(rect.Height/8, rect.Height/2);
                float k1 = (float) (0.2 + 0.2*rnd.NextDouble());
                float k2 = (float) (k1 + 0.2 - 0.4*rnd.NextDouble());
                Grass grass = new Grass(pos, new Vector2(l, l), new Vector2(k1, k2), 0.98f);
                
                data.Add(grass);
            }
        }

        public void Draw(SpriteBatchEx spriteBatch, GameTime time)
        {
            foreach (var grass in data)
            {
                grass.Draw(spriteBatch, time);
            }
        }
    }
}
