using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    public class SpriteBatchEx : SpriteBatch
    {
        Texture2D txPixel;
        //public SpriteBatchEx(GraphicsDevice graphicsDevice):base(graphicsDevice)
        //{
        //    txPixel = new Texture2D(GraphicsDevice, 1, 1);
        //    txPixel.SetData<Color>(new Color[1] { Color.White });
        //}

        public SpriteBatchEx(Microsoft.Xna.Framework.Graphics.GraphicsDevice GraphicsDevice)
            : base(GraphicsDevice)
        {
            // TODO: Complete member initialization
            txPixel = new Texture2D(GraphicsDevice, 1, 1);
            txPixel.SetData<Color>(new Color[1] { Color.White });
        }

        public void DrawLine(Vector2 start, Vector2 end, Color color, int size)
        {
            float len = (end - start).Length();

            Vector2 direction = (end - start);
            float angle = (float)Math.Atan2(direction.Y, direction.X); // try this way later
         
            Draw(txPixel, start, null, color, angle, new Vector2(0, 0), new Vector2(len, size), SpriteEffects.None, 1f);
        }

        public void DrawLine(Vector2 start, float angle, float length, Color color, int size)
        {
           
            Draw(txPixel, start, null, color, angle, new Vector2(0, 0), new Vector2(length, size), SpriteEffects.None, 1f);
        }

        public void DrawRectangle(Vector2 start, Vector2 end, Color color)
        {
            Vector2 start1=start;
            Vector2 end1=end;
            if (end.X - start.X < 0)
            {
                start1.X = end.X;
                end1.X = start.X;
                
            }
            if (end.Y - start.Y < 0)
            {
                start1.Y = end.Y;
                end1.Y=start.Y;
            }
            Draw(txPixel, start1, null, color, 0, new Vector2(0, 0), new Vector2((end1 - start1).X, (end1 - start1).Y), SpriteEffects.None, 1f);


        }

    }
}
