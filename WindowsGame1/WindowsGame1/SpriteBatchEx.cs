using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    class SpriteBatchEx : SpriteBatch
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

        public void DrawLine(Vector2 start, Vector2 end, Color color)
        {
            float len = (end - start).Length();
            int mnoz = 1;
            if ((end - start).Y < 0)
                mnoz = -1;

            float angle = mnoz * (float)Math.Acos(((end - start).X) / len);
            Draw(txPixel, start, null, Color.Black, angle, new Vector2(0, 0), new Vector2(len, 1f), SpriteEffects.None, 1f);


        }

        public void DrawRectangle(Vector2 start, Vector2 end, Color color)
        {

            Draw(txPixel, start, null, Color.Black, 0, new Vector2(0, 0), new Vector2((end - start).X, (end - start).Y), SpriteEffects.None, 1f);


        }

    }
}
