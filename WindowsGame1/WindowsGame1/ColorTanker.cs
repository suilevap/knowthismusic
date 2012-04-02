using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;

namespace WindowsGame1
{
    class ColorTanker
    {
        public Vector2 Position;
        public int maxR;
        public int maxG;
        public int maxB;
        public float curR = 0;
        public float curG = 0;
        public float curB = 0;
        public float curRrealtime = 0;
        public float curGrealtime = 0;
        public float curBrealtime = 0;
        public float veloR = 0;
        public float veloG = 0;
        public float veloB = 0;
        int rectWidth = 20;
        int zazor = 4;
        int height = 200;
        float friction = 0.96f;
        float strength = 0.002f;

        public ColorTanker(Vector2 position, int maxr, int maxg, int maxb)
        {
            Position = position;
            maxR = maxr;
            maxG = maxg;
            maxB = maxb;
            curR = maxr;
            curG = maxg;
            curB = maxb;

        }

        
        public void Minus(int index)
        {
            if (index == 0)
                curR--;
            else if (index == 1)
                curG--;
            else if (index == 2)
                curB--;
        }

        public void Draw(SpriteBatchEx spriteBatch,SpriteFont font)
        {
            if (curRrealtime != curR)
            {
                int mno = 1;
                if (curRrealtime > curR)
                    mno = 2;
                veloR += (curR - curRrealtime)*strength*mno;
                
             }
            curRrealtime += veloR;
            veloR = veloR * friction;

            if (curGrealtime != curG)
            {
                int mno = 1;
                if (curRrealtime > curR)
                    mno = 2;
                veloG += (curG - curGrealtime) * strength * mno;

            }
            curGrealtime += veloG;
            veloG = veloG * friction;
           
            if (curBrealtime != curB)
            {
                int mno = 1;
                if (curRrealtime > curR)
                    mno = 2;
                veloB += (curB - curBrealtime) * strength * mno;

            }
            curBrealtime += veloB;
            veloB = veloB * friction;

            spriteBatch.DrawRectangle(new Vector2(Position.X - rectWidth / 2f - zazor, Position.Y), new Vector2(Position.X - rectWidth * 1.5f - zazor, Position.Y - height * curRrealtime / maxR), Color.Red);
            spriteBatch.DrawRectangle(new Vector2(Position.X - rectWidth / 2f, Position.Y), new Vector2(Position.X + rectWidth /2, Position.Y - height * curGrealtime / maxG), Color.Green);
            spriteBatch.DrawRectangle(new Vector2(Position.X + rectWidth / 2f + zazor, Position.Y), new Vector2(Position.X + rectWidth * 1.5f + zazor, Position.Y - height * curBrealtime / maxB), Color.Blue);

            //string output = string.Format("{0}/{1} {2}/{3} {4}/{5}", curR, maxR, curG, maxG, curB, maxB);

            // Find the center of the string
           // Vector2 FontOrigin = font.MeasureString(output) / 2;
            // Draw the string
            //spriteBatch.DrawString(font, output, new Vector2(Position.X , Position.Y-height/2), Color.Black,0,FontOrigin,1,SpriteEffects.None,0);
 
        }
    }
}
